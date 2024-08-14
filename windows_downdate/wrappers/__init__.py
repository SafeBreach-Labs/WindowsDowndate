import ctypes
from typing import Callable, Tuple, Any

import win32api


####################
# Helper functions #
####################


def raise_if_false(result: int, func: Callable = None, arguments: Tuple[Any] = ()) -> int:
    """
    Ctypes errcheck WinAPI wrappers helper that checks result code and raises if False

    :param result: The result/return code
    :param func: The called Ctypes function
    :param arguments: The arguments to the Ctypes function
    :return: The result/return code
    """
    if not result:
        last_error = win32api.GetLastError()
        message = win32api.FormatMessage(last_error)
        raise ctypes.WinError(last_error, message)
    return result

