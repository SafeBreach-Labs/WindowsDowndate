import ctypes
from ctypes import wintypes
from typing import Callable, Tuple, Any


#############
# Constants #
#############


NULL_PTR = wintypes.LPVOID(0)


####################
# Helper functions #
####################


def raise_if_false(result: int, func: Callable = None, arguments: Tuple[Any] = ()) -> int:
    if not result:
        raise ctypes.WinError(result, "Error message here")  # TODO: Add FormatMessage
    return result

