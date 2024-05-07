import ctypes
from ctypes import wintypes

from windows_downdate.wrappers import raise_if_false


##############
# Structures #
##############


DELTA_FLAG_NONE = ctypes.c_int64(0)
P_BUFFER = ctypes.POINTER(ctypes.c_char)


class DELTA_INPUT(ctypes.Structure):
    _fields_ = [
        ("lpStart", P_BUFFER),
        ("uSize", ctypes.c_size_t),
        ("Editable", wintypes.BOOL)
    ]


class DELTA_OUTPUT(ctypes.Structure):
    _fields_ = [
        ("lpStart", P_BUFFER),
        ("uSize", ctypes.c_size_t)
    ]

    def get_buffer(self) -> bytes:
        return bytes(self.lpStart[:self.uSize])

    def __del__(self) -> None:
        if self.lpStart:
            DeltaFree(self.lpStart)


P_DELTA_OUTPUT = ctypes.POINTER(DELTA_OUTPUT)


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


#####################
# Function Wrappers #
#####################


def apply_delta(delta_file_flag: ctypes.c_int64, source: bytes, delta: bytes) -> DELTA_OUTPUT:
    source_delta_input = DELTA_INPUT()
    source_delta_input.lpStart = ctypes.create_string_buffer(source)
    source_delta_input.uSize = len(source)
    source_delta_input.Editable = False

    delta_delta_input = DELTA_INPUT()
    delta_delta_input.lpStart = ctypes.create_string_buffer(delta)
    delta_delta_input.uSize = len(delta)
    delta_delta_input.Editable = False

    target_delta_output = DELTA_OUTPUT()

    ApplyDeltaB(delta_file_flag, source_delta_input, delta_delta_input, ctypes.byref(target_delta_output))

    return target_delta_output
