import ctypes
from ctypes import wintypes
from typing import Callable, Tuple, Any
from abc import ABCMeta

##############
# Structures #
##############


DELTA_FLAG_NONE = ctypes.c_int64(0)
P_BUFFER = ctypes.POINTER(ctypes.c_char)


class DeltaStructure(ctypes.Structure):
    def get_buffer(self) -> bytes:
        return bytes(self.lpStart[:self.uSize])


class DELTA_INPUT(DeltaStructure):
    _fields_ = [
        ("lpStart", P_BUFFER),
        ("uSize", ctypes.c_size_t),
        ("Editable", wintypes.BOOL)
    ]


class DELTA_OUTPUT(DeltaStructure):
    _fields_ = [
        ("lpStart", P_BUFFER),
        ("uSize", ctypes.c_size_t)
    ]

    def __del__(self) -> None:
        if self.lpStart:
            DeltaFree(self.lpStart)


P_DELTA_OUTPUT = ctypes.POINTER(DELTA_OUTPUT)


##################
# Error handlers #
##################


def raise_if_false(result: int, func: Callable = None, arguments: Tuple[Any] = ()) -> int:
    if not result:
        raise ctypes.WinError(result, "Error message here")  # TODO: Add FormatMessage
    return result


########################
# Function definitions #
########################

# TODO: Move definition to wrapper (?)
ApplyDeltaB = ctypes.windll.msdelta.ApplyDeltaB
ApplyDeltaB.argstypes = [ctypes.c_int64, DELTA_INPUT, DELTA_INPUT, P_DELTA_OUTPUT]
ApplyDeltaB.restype = wintypes.BOOL
ApplyDeltaB.errcheck = raise_if_false

# TODO: Add wrapper
DeltaFree = ctypes.windll.msdelta.DeltaFree
DeltaFree.argstypes = [P_BUFFER]
DeltaFree.restype = wintypes.BOOL
DeltaFree.errcheck = raise_if_false
