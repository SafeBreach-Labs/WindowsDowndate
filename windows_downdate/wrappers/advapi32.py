import ctypes
from ctypes import wintypes
from typing import Union

import pywintypes

from windows_downdate.wrappers import raise_if_false, NULL_PTR, convert_pyhandle_to_handle
from windows_downdate.wrappers.kernel32 import P_PROCESS_INFORMATION, PROCESS_INFORMATION, P_STARTUPINFOW, STARTUPINFOW


#############
# Constants #
#############


LOGON_WITH_PROFILE = 1
LOGON_NETCREDENTIALS_ONLY = 2


##############
# Structures #
##############


class SID_IDENTIFIER_AUTHORITY(ctypes.Structure):
    _fields_ = [
        ('Value', wintypes.BYTE * 6),
    ]


PSID_IDENTIFIER_AUTHORITY = ctypes.POINTER(SID_IDENTIFIER_AUTHORITY)


class SID(ctypes.Structure):
    _fields_ = [
        ('Revision', wintypes.BYTE),
        ('SubAuthorityCount', wintypes.BYTE),
        ('IdentifierAuthority', SID_IDENTIFIER_AUTHORITY),
        ('SubAuthority', wintypes.DWORD * 16),
    ]


P_SID = ctypes.POINTER(SID)


########################
# Function definitions #
########################


CreateProcessWithTokenW = ctypes.windll.advapi32.CreateProcessWithTokenW
CreateProcessWithTokenW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, wintypes.LPWSTR, wintypes.DWORD,
                                    wintypes.LPVOID, wintypes.LPWSTR, P_STARTUPINFOW, P_PROCESS_INFORMATION]
CreateProcessWithTokenW.restype = wintypes.BOOL
CreateProcessWithTokenW.errcheck = raise_if_false


CheckTokenMembership = ctypes.windll.advapi32.CheckTokenMembership
CheckTokenMembership.restype = wintypes.BOOL
CheckTokenMembership.argtypes = [wintypes.HANDLE, P_SID, wintypes.PBOOL]
CheckTokenMembership.errcheck = raise_if_false


#####################
# Function Wrappers #
#####################


def create_process_with_token(token_handle: Union[int, pywintypes.HANDLE],
                              logon_flags: wintypes.DWORD = 0,
                              application_name: str = None,
                              command_line: str = None,
                              creation_flags: int = 0,
                              environment: wintypes.LPVOID = NULL_PTR,
                              current_directory: str = None,
                              startup_info: STARTUPINFOW = STARTUPINFOW(),
                              process_info: PROCESS_INFORMATION = PROCESS_INFORMATION()) -> None:
    token_handle = convert_pyhandle_to_handle(token_handle)

    if application_name:
        application_name = ctypes.create_unicode_buffer(application_name)

    if command_line:
        command_line = ctypes.create_unicode_buffer(command_line)

    if current_directory:
        current_directory = ctypes.create_unicode_buffer(current_directory)

    CreateProcessWithTokenW(token_handle, logon_flags, application_name, command_line, creation_flags, environment,
                            current_directory, ctypes.byref(startup_info), ctypes.byref(process_info))


def check_token_membership(token_handle: Union[int, pywintypes.HANDLE], sid: SID) -> bool:
    token_handle = convert_pyhandle_to_handle(token_handle)

    is_member = wintypes.BOOL()
    CheckTokenMembership(token_handle, ctypes.byref(sid), ctypes.byref(is_member))
    return bool(is_member.value)
