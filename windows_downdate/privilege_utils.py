from typing import List, Tuple

import pywintypes
import win32api
import win32con
import win32security
import winerror

from windows_downdate.process_utils import get_process_id_by_name
from windows_downdate.service_utils import start_service
from windows_downdate.wrappers.advapi32 import check_token_membership
from windows_downdate.wrappers.ntdll import rtl_create_service_sid


def convert_privilege_name_to_luid(privilege: Tuple[str, int]) -> Tuple[int, int]:
    privilege_name, privilege_attrs = privilege
    luid = win32security.LookupPrivilegeValue(None, privilege_name)

    return luid, privilege_attrs


def adjust_token_privileges(privileges: List[Tuple[str, int]], disable_all_privileges_flag: bool = False) -> None:
    privileges_with_luids = [convert_privilege_name_to_luid(privilege) for privilege in privileges]
    token_handle = win32security.OpenProcessToken(win32api.GetCurrentProcess(),
                                                  win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY)
    win32security.AdjustTokenPrivileges(token_handle, disable_all_privileges_flag, privileges_with_luids)


def enable_privilege(privilege_name: str) -> None:
    privilege = [(privilege_name, win32security.SE_PRIVILEGE_ENABLED)]
    adjust_token_privileges(privilege)


def impersonate_process_by_process_name(process_name: str) -> None:
    """
    TODO:
        read more about ImpersonateLoggedOnUser, and how pywin32 implements it. It may fail sometimes without raising
        The behavior encountered is that without SeImpersonate, calling ImpersonateLoggedOnUser wont fail
        While the actual impersonation is not successful
        If SeImpersonate is enabled, the impersonation is successful
    """

    process_id = get_process_id_by_name(process_name)
    process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, process_id)
    process_token_handle = win32security.OpenProcessToken(process_handle, win32con.TOKEN_DUPLICATE)
    dup_process_token_handle = win32security.DuplicateTokenEx(process_token_handle,
                                                              win32security.SecurityImpersonation,
                                                              win32con.TOKEN_ALL_ACCESS,
                                                              win32security.TokenImpersonation,
                                                              win32security.SECURITY_ATTRIBUTES())
    win32security.ImpersonateLoggedOnUser(dup_process_token_handle)


def impersonate_nt_system() -> None:
    impersonate_process_by_process_name("winlogon.exe")


def impersonate_trusted_installer() -> None:
    impersonate_nt_system()
    enable_privilege(win32security.SE_IMPERSONATE_NAME)
    start_service("TrustedInstaller")
    impersonate_process_by_process_name("TrustedInstaller.exe")


def is_trusted_installer() -> bool:
    try:
        thread_token = win32security.OpenThreadToken(win32api.GetCurrentThread(), win32security.TOKEN_QUERY, False)
    except pywintypes.error as e:
        if e.winerror == winerror.ERROR_NO_TOKEN:
            return False
        raise

    trusted_installer_sid = rtl_create_service_sid("TrustedInstaller")
    # Not using win32security.CheckTokenMembership because PySid is not properly documented
    return check_token_membership(thread_token, trusted_installer_sid)


def is_administrator() -> bool:
    administrator_sid = win32security.CreateWellKnownSid(win32security.WinBuiltinAdministratorsSid)
    return win32security.CheckTokenMembership(None, administrator_sid)
