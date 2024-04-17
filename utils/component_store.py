import os.path
import re
import shutil
import winreg
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List

from utils.filesystem import read_file, list_dirs, is_path_exists, write_file, Path
from utils.privilege import enable_backup_privilege, enable_restore_privilege
from utils.xml_utils import load_xml_from_buffer, find_child_elements_by_match, get_element_attribute, \
    XmlElementNotFound, XmlElementAttributeNotFound
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
    # "runtime.documentssettings": "C:\\Users\\weak\\Desktop\\DocumentSettings",  # TODO: Resolve to garbage dir
    "runtime.inf": "%SystemRoot%\\INF",
    "runtime.commonfiles": "%CommonProgramFiles%",
    "runtime.windows": "%SystemRoot%",
    # "runtime.userprofile": "C:\\Users\\weak\\Desktop\\UserProfile",  # TODO: Resolve to garbage dir
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


# TODO: Think of the proper file to place this class in
@dataclass
class UpdateFile:

    source: Path
    destination: Path
    should_retrieve_oldest: bool
    is_oldest_retrieved: bool

    def to_hardlink_dict(self):
        return {"source": self.source.nt_path, "destination": self.destination.nt_path}


# TODO: Reconsider XML exceptions

class Manifest:

    BASE_MANIFEST = read_file("resources\\WcpBaseManifest.xml")
    DCM_HEADER = b"DCM\x01"

    def __init__(self, manifest_name: str) -> None:
        self._manifest_name = manifest_name
        self._manifest_path = f"{COMPONENT_STORE_MANIFESTS_PATH}\\{manifest_name}.manifest"
        self._manifest_buffer = None
        self._manifest_xml = None
        self._manifest_files = None

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

    def get_manifest_files(self) -> List[str]:
        if not self._manifest_files:
            self._manifest_files = []
            manifest_xml = self.get_manifest_xml()
            # TODO: For attribute errors, I may throw everything while the next file element can be valid
            try:
                for file_element in find_child_elements_by_match(manifest_xml, "{urn:schemas-microsoft-com:asm.v3}file"):
                    update_dir_path = get_element_attribute(file_element, "destinationPath")
                    update_dir_path_exp = expand_package_variables(update_dir_path)
                    update_file_name = get_element_attribute(file_element, "name")
                    update_file_path = os.path.normpath(fr"{update_dir_path_exp}\{update_file_name}")
                    self._manifest_files.append(update_file_path)
            except (XmlElementNotFound, XmlElementAttributeNotFound):
                pass  # TODO: Make sure I am not missing anything here, especially for files with no DestinationPath

        return self._manifest_files

    def is_file_in_manifest_files(self, file_to_search: str) -> bool:
        for manifest_file in self.get_manifest_files():
            if manifest_file.lower() == file_to_search.lower():
                return True
        return False

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
        raise Exception(f"Did not find component directories in component store")

    return components


def retrieve_oldest_files_for_update_files(update_files: List[UpdateFile]) -> None:

    for component in get_components():

        for update_file in update_files:
            if not update_file.should_retrieve_oldest or update_file.is_oldest_retrieved:
                continue

            manifest = Manifest(component.name)
            if not manifest.is_file_in_manifest_files(update_file.destination.full_path):
                continue

            updated_file_path = f"{component.full_path}\\{update_file.destination.name}"
            reverse_diff_file_path = f"{component.full_path}\\r\\{update_file.destination.name}"

            # If there is reverse diff, apply it to create the base file
            if is_path_exists(reverse_diff_file_path):
                updated_file_content = read_file(updated_file_path)
                reverse_diff_file_content = read_file(reverse_diff_file_path)[4:]  # Remove CRC checksum
                base_delta_output_obj = apply_delta(DELTA_FLAG_NONE, updated_file_content, reverse_diff_file_content)
                base_content = base_delta_output_obj.get_buffer()
                write_file(update_file.source.full_path, base_content)

            # If there is no reverse diff, the update file is the oldest file available
            else:
                shutil.copyfile(updated_file_path, update_file.source.full_path)

            update_file.is_oldest_retrieved = True

    for update_file in update_files:
        if update_file.should_retrieve_oldest and not update_file.is_oldest_retrieved:
            raise Exception("Oldest destination file retrieval failed. "
                            f"Destination {update_file.destination.name} is not part of the component store")


# TODO: Do I actually need regex for it?
def expand_package_variables(str_to_expand: str) -> str:
    pattern = r'\$\(([^)]+)\)'

    def replace(match):
        variable_name = match.group(1).lower()
        return PACKAGE_VARIABLES.get(variable_name, match.group(0))  # TODO: Add logs to find unknown variables

    expanded_str = re.sub(pattern, replace, str_to_expand)
    return os.path.expandvars(expanded_str)


def load_components_hive() -> None:
    # Make sure the required privileges for loading the hive are held
    enable_backup_privilege()
    enable_restore_privilege()

    components_hive_path_exp = os.path.expandvars(COMPONENTS_HIVE_PATH)
    winreg.LoadKey(winreg.HKEY_LOCAL_MACHINE, "COMPONENTS", components_hive_path_exp)
