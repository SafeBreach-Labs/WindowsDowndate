import ctypes
from ctypes import wintypes
from typing import Callable, Tuple, Any

from windows_downdate.wrappers.advapi32 import P_SID, SID


#############
# Constants #
#############


NTSTATUS = wintypes.LONG
STATUS_SUCCESS = 0x00000000


##############
# Structures #
##############


class UNICODE_STRING(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.USHORT),
        ("MaximumLength", wintypes.USHORT),
        ("Buffer", wintypes.PWCHAR)
    ]

    def get_string(self) -> str:
        return ctypes.string_at(self.Buffer, self.Length).decode('utf-16-le')


P_UNICODE_STRING = ctypes.POINTER(UNICODE_STRING)


####################
# Helper functions #
####################


def check_nt_status(nt_status: int, func: Callable = None, arguments: Tuple[Any] = ()) -> int:
    if nt_status < STATUS_SUCCESS:
        raise ctypes.WinError(nt_status, "Error message here")  # TODO: Add NTSTATUS error messages

    return nt_status


def init_unicode_string(string: str) -> UNICODE_STRING:
    string = string.encode('utf-16-le')
    unicode_string = UNICODE_STRING()
    unicode_string.Buffer = ctypes.cast(ctypes.create_string_buffer(string), ctypes.POINTER(wintypes.WCHAR))
    unicode_string.Length = len(string)
    unicode_string.MaximumLength = len(string) + 2

    return unicode_string


########################
# Function definitions #
########################


RtlCreateServiceSid = ctypes.windll.ntdll.RtlCreateServiceSid
RtlCreateServiceSid.argtypes = [P_UNICODE_STRING, P_SID, wintypes.PULONG]
RtlCreateServiceSid.restype = NTSTATUS
RtlCreateServiceSid.errcheck = check_nt_status


#####################
# Function Wrappers #
#####################


# TODO: Add length error handling
# TODO: Convert return type to pywintypes.SID to make it compatible with PyWin32
def rtl_create_service_sid(service_name: str) -> SID:
    unicode_service_name = init_unicode_string(service_name)
    sid = SID()
    sid_length = wintypes.ULONG(72)
    RtlCreateServiceSid(ctypes.byref(unicode_service_name), ctypes.byref(sid), ctypes.byref(sid_length))

    return sid
