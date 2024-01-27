from typing import List, Tuple

import win32api
import win32security


def convert_privilege_name_to_luid(privilege: Tuple[str, int]) -> Tuple[int, int]:
    privilege_name, privilege_attrs = privilege
    luid = win32security.LookupPrivilegeValue(None, privilege_name)

    return luid, privilege_attrs


def adjust_token_privileges(privileges: List[Tuple[str, int]], disable_all_privileges_flag: bool = False) -> None:
    privileges_with_luids = [convert_privilege_name_to_luid(privilege) for privilege in privileges]
    token_handle = win32security.OpenProcessToken(win32api.GetCurrentProcess(),
                                                  win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY)
    win32security.AdjustTokenPrivileges(token_handle, disable_all_privileges_flag, privileges_with_luids)


def enable_backup_privilege() -> None:
    privileges = [(win32security.SE_BACKUP_NAME, win32security.SE_PRIVILEGE_ENABLED)]
    adjust_token_privileges(privileges)


def enable_restore_privilege() -> None:
    privilege = [(win32security.SE_RESTORE_NAME, win32security.SE_PRIVILEGE_ENABLED)]
    adjust_token_privileges(privilege)
