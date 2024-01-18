import os.path
import re
import xml.etree.ElementTree as ET
from typing import List

from filesystem_utils import list_files_by_extensions, read_file, list_dirs, DirectoryNotFound
from ms_delta import apply_delta
from ms_delta_definitions import DELTA_FLAG_NONE
from xml_utils import load_xml_from_buffer

COMPONENT_STORE_PATH = "%SystemRoot%\\WinSxS\\"
COMPONENT_STORE_MANIFESTS_PATH = "%SystemRoot%\\WinSxS\\Manifests\\"
COMPONENT_STORE_WINNERS_REGISTRY_PATH = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\SideBySide\\Winners"

COMPONENT_DIR_PREFIXES = ["amd64", "msil", "wow64", "x86"]

PACKAGE_VARIABLES = {
    "runtime.programfilesx86": "%ProgramFiles(x86)%",
    "runtime.help": "%SystemRoot%\\Help",
    "runtime.bootdrive": "%SystemDrive%",
    "runtime.systemroot": "%SystemRoot%",
    "runtime.documentssettings": "C:\\Users\\weak\\Desktop\\BYOVW\\Temp",  # TODO: Resolve to garbage dir
    "runtime.inf": "%SystemRoot%\\INF",
    "runtime.commonfiles": "%CommonProgramFiles%",
    "runtime.windows": "%SystemRoot%",
    "runtime.userprofile": "C:\\Users\\weak",  # TODO: Resolve to garbage dir
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

    BASE_MANIFEST = read_file("BYOVW\\resources\\WcpBaseManifest.xml")
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

    def get_manifest_files(self) -> List[str]:
        pass

    @staticmethod
    def decompress_manifest(manifest_buffer: bytes) -> bytes:
        manifest_buffer_without_dcm = manifest_buffer[4:]  # Remove DCM header
        manifest_delta_output_obj = apply_delta(DELTA_FLAG_NONE, Manifest.BASE_MANIFEST, manifest_buffer_without_dcm)
        return manifest_delta_output_obj.get_buffer()


def get_all_manifest_names() -> List[str]:
    return list_files_by_extensions(COMPONENT_STORE_MANIFESTS_PATH, ".manifest")


def is_component_dir(dir_name: str, case_sensitive: bool = False) -> bool:
    for prefix in COMPONENT_DIR_PREFIXES:
        if not case_sensitive:
            dir_name = dir_name.lower()
            prefix = prefix.lower()

        return dir_name.startswith(prefix)


def get_components() -> List[str]:
    components = []
    for component_store_dir in list_dirs(COMPONENT_STORE_PATH, return_name_only=True, oldest_to_newest=True):
        if is_component_dir(component_store_dir):
            components.append(component_store_dir)

    if not components:
        raise Exception(f"Did not find side by side directories in component store")

    return components


def create_base_update_files() -> None:

    for component in get_components():
        component_manifest = Manifest(component)

        # Get all component files

        # Iterate over each one, and query against manifest
        # If not found, raise exception

        # If found, create base in a base dir

        # Make sure base is not the same as target file, if same abort delete base

        # Add to base files dict/list

        # Add to pending.xml


# TODO: This should be the API decompressing ?
def get_manifest_names_per_build(os_build_number: str) -> List[str]:
    manifests = get_all_manifest_names()
    manifests_per_build = []
    for manifest in manifests:
        if f"{os_build_number}_" in manifest:
            manifests_per_build.append(manifest)

    if not manifests_per_build:
        raise Exception(f"Did not find manifest files for build number: {os_build_number}")

    return manifests_per_build


# TODO: Do I actually need regex for it?
def expand_package_variables(str_to_expand: str) -> str:
    pattern = r'\$\(([^)]+)\)'

    def replace(match):
        variable_name = match.group(1).lower()
        return PACKAGE_VARIABLES.get(variable_name, match.group(0))  # TODO: Add logs to find unknown variables

    expanded_str = re.sub(pattern, replace, str_to_expand)
    return os.path.expandvars(expanded_str)
