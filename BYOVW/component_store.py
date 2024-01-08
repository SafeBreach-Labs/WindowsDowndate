import os.path
import re
from typing import List

from filesystem_utils import list_files_by_extensions, read_file
from ms_delta_definitions import DELTA_OUTPUT, DELTA_FLAG_NONE
from ms_delta import apply_delta


COMPONENT_STORE_PATH = "%SystemRoot%\\WinSxS\\"
COMPONENT_STORE_MANIFESTS_PATH = "%SystemRoot%\\WinSxS\\Manifests\\"

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


def get_all_manifest_names() -> List[str]:
    return list_files_by_extensions(COMPONENT_STORE_MANIFESTS_PATH, ".manifest")


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


def decompress_manifest(manifest_name: str) -> DELTA_OUTPUT:
    # TODO: Load WCP base manifest dynamically from WCP.DLL, in case it changes in the future
    # TODO: For each manifest, I read this again and again and again, but its hardcoded
    base_manifest_contents = read_file("resources\\WcpBaseManifest.xml")
    manifest_contents = read_file(f"{COMPONENT_STORE_MANIFESTS_PATH}\\{manifest_name}")[4:]  # Remove DCM header

    decompressed_manifest = apply_delta(DELTA_FLAG_NONE, base_manifest_contents, manifest_contents)

    return decompressed_manifest


# TODO: Do I actually need regex for it?
def expand_package_variables(str_to_expand: str) -> str:
    pattern = r'\$\(([^)]+)\)'

    def replace(match):
        variable_name = match.group(1).lower()
        return PACKAGE_VARIABLES.get(variable_name, match.group(0))  # TODO: Add logs to find unknown variables

    expanded_str = re.sub(pattern, replace, str_to_expand)
    return os.path.expandvars(expanded_str)
