import os
import re
import xml.etree.ElementTree as ET
from typing import List

import win32api

from windows_downdate.filesystem_utils import read_file
from windows_downdate.update_utils import get_servicing_stack_path
from windows_downdate.resource_utils import get_first_resource_language
from windows_downdate.wrappers.ms_delta import apply_delta, DELTA_FLAG_NONE
from windows_downdate.xml_utils import load_xml_from_buffer, find_child_elements_by_match, get_element_attribute, \
    XmlElementAttributeNotFound


RT_WCP_BASE_MANIFEST = 614
RN_WCP_BASE_MANIFEST = 1


def get_wcp_base_manifest() -> bytes:
    servicing_stack_path = get_servicing_stack_path()
    wcp_dll_path = f"{servicing_stack_path}\\wcp.dll"
    wcp_module = win32api.LoadLibrary(wcp_dll_path)
    return get_first_resource_language(wcp_module, RT_WCP_BASE_MANIFEST, RN_WCP_BASE_MANIFEST)


class Manifest:

    BASE_MANIFEST = get_wcp_base_manifest()

    DCM_HEADER = b"DCM\x01"

    COMPONENT_STORE_MANIFESTS_PATH = "%SystemRoot%\\WinSxS\\Manifests\\"

    PACKAGE_VARIABLES = {
        "runtime.programfilesx86": "%ProgramFiles(x86)%",
        "runtime.help": "%SystemRoot%\\Help",
        "runtime.bootdrive": "%SystemDrive%",
        "runtime.systemroot": "%SystemRoot%",
        "runtime.inf": "%SystemRoot%\\INF",
        "runtime.commonfiles": "%CommonProgramFiles%",
        "runtime.windows": "%SystemRoot%",
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

    def __init__(self, manifest_name: str) -> None:
        self._manifest_name = manifest_name
        self._manifest_path = f"{Manifest.COMPONENT_STORE_MANIFESTS_PATH}\\{manifest_name}.manifest"
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
            if self._is_manifest_diff_type():
                self._manifest_buffer = self._decompress_manifest()
        return self._manifest_buffer

    def get_manifest_files(self) -> List[str]:
        if not self._manifest_files:
            self._manifest_files = []
            manifest_xml = self.get_manifest_xml()
            for file_element in find_child_elements_by_match(manifest_xml, "{urn:schemas-microsoft-com:asm.v3}file"):
                try:
                    update_dir_path = get_element_attribute(file_element, "destinationPath")
                    update_dir_path_exp = self.expand_manifest_path_variables(update_dir_path)
                    update_file_name = get_element_attribute(file_element, "name")
                    update_file_path = os.path.normpath(fr"{update_dir_path_exp}\{update_file_name}")
                    self._manifest_files.append(update_file_path)
                except XmlElementAttributeNotFound:
                    # If there is no destinationPath or no Name to the file entry, skip entry
                    continue

        return self._manifest_files

    def is_file_in_manifest_files(self, file_to_search: str) -> bool:
        for manifest_file in self.get_manifest_files():
            if manifest_file.lower() == file_to_search.lower():
                return True
        return False

    def _decompress_manifest(self) -> bytes:
        manifest_buffer = self.get_manifest_buffer()
        manifest_buffer_without_dcm = manifest_buffer[4:]  # Remove DCM header
        decompressed_manifest = apply_delta(DELTA_FLAG_NONE, Manifest.BASE_MANIFEST, manifest_buffer_without_dcm)
        return decompressed_manifest

    def _is_manifest_diff_type(self) -> bool:
        manifest_buffer = self.get_manifest_buffer()
        return manifest_buffer.startswith(Manifest.DCM_HEADER)

    @staticmethod
    def expand_manifest_path_variables(str_to_expand: str) -> str:
        pattern = r'\$\(([^)]+)\)'

        def replace(match):
            variable_name = match.group(1).lower()
            full_name = match.group(0)
            return Manifest.PACKAGE_VARIABLES.get(variable_name, full_name)  # If didn't find variable value, do nothing

        expanded_str = re.sub(pattern, replace, str_to_expand)
        return os.path.expandvars(expanded_str)
