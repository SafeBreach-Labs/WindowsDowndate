import ctypes
from ctypes import wintypes
from typing import Callable, Tuple, Any, Union

import pywintypes


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


def convert_pyhandle_to_handle(token_handle: Union[int, pywintypes.HANDLE]) -> int:
    if isinstance(token_handle, pywintypes.HANDLEType):
        token_handle = token_handle.handle
    return token_handle
