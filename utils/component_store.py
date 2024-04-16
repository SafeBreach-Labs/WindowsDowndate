import os.path
import re
import winreg
import xml.etree.ElementTree as ET
from typing import List, Dict

from utils.filesystem import read_file, list_dirs, is_path_exists, write_file, Path
from utils.privilege import enable_backup_privilege, enable_restore_privilege
from utils.xml import load_xml_from_buffer, find_child_elements_by_match, get_element_attribute, \
    XmlElementAttributeNotFound, XmlElementNotFound
from wrappers.ms_delta import apply_delta
from wrappers.ms_delta_definitions import DELTA_FLAG_NONE

COMPONENT_STORE_PATH = "%SystemRoot%\\WinSxS\\"
COMPONENT_STORE_MANIFESTS_PATH = "%SystemRoot%\\WinSxS\\Manifests\\"
COMPONENTS_HIVE_PATH = "%SystemRoot%\\System32\\Config\\COMPONENTS"

COMPONENT_DIR_PREFIXES = ["amd64", "msil", "wow64", "x86"]

PACKAGE_VARIABLES = {
    "runtime.programfilesx86": "%ProgramFiles(x86)%",
    "runtime.help": "%SystemRoot%\\Help",
    "runtime.bootdrive": "%SystemDrive%",
    "runtime.systemroot": "%SystemRoot%",
    "runtime.documentssettings": "C:\\Users\\weak\\Desktop\\DocumentSettings",  # TODO: Resolve to garbage dir
    "runtime.inf": "%SystemRoot%\\INF",
    "runtime.commonfiles": "%CommonProgramFiles%",
    "runtime.windows": "%SystemRoot%",
    "runtime.userprofile": "C:\\Users\\weak\\Desktop\\UserProfile",  # TODO: Resolve to garbage dir
    "runtime.public": "%Public%",
    "runtime.system": "%SystemRoot%\\System",
    "runtime.programdata": "%ProgramData%",
    "runtime.wbem": "%SystemRoot%\\System32\\wbem",
    "runtime.startmenu": "%ProgramData%\\Microsoft\\Windows\\Start Menu",
    "runtime.fonts": "%SystemRoot%\\Fonts",
    "runtime.windir": "%SystemRoot%",
    "runtime.system32": "%SystemRoot%\\System32",
    "runtime.programfiles": "%ProgramFiles%",
    "runtime.drivers": "%SystemRoot%\\System32\\Drivers"
}


class Manifest:

    BASE_MANIFEST = read_file("resources\\WcpBaseManifest.xml")
    DCM_HEADER = b"DCM\x01"

    def __init__(self, manifest_name: str) -> None:
        self._manifest_name = manifest_name
        self._manifest_path = f"{COMPONENT_STORE_MANIFESTS_PATH}\\{manifest_name}.manifest"
        self._manifest_buffer = None
        self._manifest_xml = None

    def get_manifest_xml(self) -> ET.ElementTree:
        if not self._manifest_xml:
            manifest_buffer = self.get_manifest_buffer()
            self._manifest_xml = load_xml_from_buffer(manifest_buffer)
        return self._manifest_xml

    def get_manifest_buffer(self) -> bytes:
        if not self._manifest_buffer:
            self._manifest_buffer = read_file(self._manifest_path)
            if self._manifest_buffer.startswith(Manifest.DCM_HEADER):
                self._manifest_buffer = self.decompress_manifest(self._manifest_buffer)
        return self._manifest_buffer

    def get_manifest_files(self) -> Dict[str, str]:
        manifest_files = {}
        manifest_xml = self.get_manifest_xml()
        for file_element in find_child_elements_by_match(manifest_xml, "{urn:schemas-microsoft-com:asm.v3}file"):
            update_dir_path = get_element_attribute(file_element, "destinationPath")
            update_dir_path_exp = expand_package_variables(update_dir_path)
            update_file_name = get_element_attribute(file_element, "name")
            update_file_path = os.path.normpath(fr"\??\{update_dir_path_exp}\{update_file_name}")
            manifest_files[update_file_name] = update_file_path

        return manifest_files

    @staticmethod
    def decompress_manifest(manifest_buffer: bytes) -> bytes:
        manifest_buffer_without_dcm = manifest_buffer[4:]  # Remove DCM header
        manifest_delta_output_obj = apply_delta(DELTA_FLAG_NONE, Manifest.BASE_MANIFEST, manifest_buffer_without_dcm)
        return manifest_delta_output_obj.get_buffer()


def is_component_dir(dir_name: str, case_sensitive: bool = False) -> bool:
    for prefix in COMPONENT_DIR_PREFIXES:
        if not case_sensitive:
            dir_name = dir_name.lower()
            prefix = prefix.lower()

        return dir_name.startswith(prefix)


def get_components() -> List[Path]:
    components = []
    for component_store_dir in list_dirs(COMPONENT_STORE_PATH, oldest_to_newest=True):
        if is_component_dir(component_store_dir.name):
            components.append(component_store_dir)

    if not components:
        raise Exception(f"Did not find side by side directories in component store")

    return components


def get_component_files(component_path: str) -> List[str]:
    component_files = []
    for root, dirs, files in os.walk(component_path):
        dirs[:] = [d for d in dirs if d not in ["f", "r", "n"]]

        for file in files:
            component_file_tree = os.path.join(root, file).split(component_path)[1]

            # Skip null files, since they have been added after base
            if is_path_exists(f"{component_path}\\n{component_file_tree}"):
                continue

            component_files.append(component_file_tree)

    return component_files


# For skipped components the path may differ from base and not base. So the tool creates the not base path and places
# The base in there, but the actual base path does not exist
def create_base_update_files(base_dir: str) -> List[Dict[str, str]]:

    base_files = []
    destination_files = []

    for component in get_components():
        try:
            manifest = Manifest(component.name)
            manifest_files = manifest.get_manifest_files()
        except (XmlElementAttributeNotFound, XmlElementNotFound):
            continue

        for file in get_component_files(component.full_path):
            destination = manifest_files[file[1:]]
            if destination in destination_files:
                continue  # We already have entry updating this file

            updated_file_path = f"{component.full_path}{file}"
            base_file_path = updated_file_path
            reverse_diff_file_path = f"{component.full_path}\\r{file}"

            # If there is reverse diff, apply it and create the base file
            if is_path_exists(reverse_diff_file_path):
                updated_file_content = read_file(updated_file_path)
                reverse_diff_file_content = read_file(reverse_diff_file_path)[4:]  # Remove CRC checksum
                try:
                    base_delta_output_obj = apply_delta(DELTA_FLAG_NONE, updated_file_content, reverse_diff_file_content)
                except:
                    print(f"[WARNING] {destination}")
                    continue
                base_content = base_delta_output_obj.get_buffer()
                base_file_path = os.path.normpath(fr"{base_dir}\{component.name}\{file}")
                os.makedirs(os.path.dirname(base_file_path), exist_ok=True)
                write_file(base_file_path, base_content)

            base_files.append({"source": base_file_path, "destination": destination})
            destination_files.append(destination)

    return base_files


# TODO: Do I actually need regex for it?
def expand_package_variables(str_to_expand: str) -> str:
    pattern = r'\$\(([^)]+)\)'

    def replace(match):
        variable_name = match.group(1).lower()
        return PACKAGE_VARIABLES.get(variable_name, match.group(0))  # TODO: Add logs to find unknown variables

    expanded_str = re.sub(pattern, replace, str_to_expand)
    return os.path.expandvars(expanded_str)


# TODO: Make an RAII wrapper for the loaded hive
def load_components_hive() -> None:
    # Make sure the required privileges for loading the hive are held
    enable_backup_privilege()
    enable_restore_privilege()

    components_hive_path_exp = os.path.expandvars(COMPONENTS_HIVE_PATH)
    winreg.LoadKey(winreg.HKEY_LOCAL_MACHINE, "COMPONENTS", components_hive_path_exp)
