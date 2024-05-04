import ctypes
from typing import Callable, Tuple, Any


def raise_if_false(result: int, func: Callable = None, arguments: Tuple[Any] = ()) -> int:
    if not result:
        raise ctypes.WinError(result, "Error message here")  # TODO: Add FormatMessage
    return result
