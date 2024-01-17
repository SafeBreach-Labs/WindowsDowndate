import os.path
import re
import xml.etree.ElementTree as ET
from typing import List

from filesystem_utils import list_files_by_extensions, read_file, list_dirs
from ms_delta import apply_delta
from ms_delta_definitions import DELTA_OUTPUT, DELTA_FLAG_NONE
from xml_utils import load_xml_from_buffer

COMPONENT_STORE_PATH = "%SystemRoot%\\WinSxS\\"
COMPONENT_STORE_MANIFESTS_PATH = "%SystemRoot%\\WinSxS\\Manifests\\"
COMPONENT_STORE_WINNERS_REGISTRY_PATH = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\SideBySide\\Winners"

SIDE_BY_SIDE_DIRECTORY_PREFIXES = ["amd64", "msil", "wow64", "x86"]

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

    def __init__(self, manifest_name: str) -> None:
        self._manifest_name = manifest_name
        self._manifest_file_name = f"{manifest_name}.manifest"
        self._manifest_buffer = None
        self._manifest_xml = None

    def get_manifest_xml(self) -> ET.ElementTree:
        if not self._manifest_xml:
            manifest_buffer = self.get_manifest_buffer()
            self._manifest_xml = load_xml_from_buffer(manifest_buffer)
        return self._manifest_xml

    def get_manifest_buffer(self) -> bytes:
        if not self._manifest_buffer:
            manifest_delta_output_obj = Manifest.decompress_manifest(self._manifest_file_name)
            self._manifest_buffer = manifest_delta_output_obj.get_buffer()
        return self._manifest_buffer

    def get_manifest_files(self) -> List[str]:
        pass

    @staticmethod
    def decompress_manifest(manifest_file_name: str) -> DELTA_OUTPUT:
        manifest_contents = read_file(f"{COMPONENT_STORE_MANIFESTS_PATH}\\{manifest_file_name}")[4:] # Remove DCM header
        return apply_delta(DELTA_FLAG_NONE, Manifest.BASE_MANIFEST, manifest_contents)


def get_all_manifest_names() -> List[str]:
    return list_files_by_extensions(COMPONENT_STORE_MANIFESTS_PATH, ".manifest")


def is_side_by_side_dir(dir_name: str, case_sensitive: bool = False) -> bool:
    for prefix in SIDE_BY_SIDE_DIRECTORY_PREFIXES:
        if not case_sensitive:
            dir_name = dir_name.lower()
            prefix = prefix.lower()

        return dir_name.startswith(prefix)


def get_side_by_side_dirs() -> List[str]:
    side_by_side_dirs = []
    for component_store_dir in list_dirs(COMPONENT_STORE_PATH, return_name_only=True):
        if is_side_by_side_dir(component_store_dir):
            side_by_side_dirs.append(component_store_dir)

    if not side_by_side_dirs:
        raise Exception(f"Did not find side by side directories in component store")

    return side_by_side_dirs


def is_diff_side_by_side(dir_path: str) -> bool:
    pass


def create_base_update_files() -> None:

    for side_by_side_dir in get_side_by_side_dirs():
        side_by_side_manifest = Manifest(side_by_side_dir)
        print(side_by_side_manifest.get_manifest_buffer())

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
