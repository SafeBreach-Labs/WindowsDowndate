import ctypes
from ctypes import wintypes
from typing import Callable, Tuple, Any

import win32api

#############
# Constants #
#############


NULL_PTR = wintypes.LPVOID(0)


####################
# Helper functions #
####################


def raise_if_false(result: int, func: Callable = None, arguments: Tuple[Any] = ()) -> int:
    if not result:
        last_error = win32api.GetLastError()
        message = win32api.FormatMessage(last_error)
        raise ctypes.WinError(last_error, message)
    return result

