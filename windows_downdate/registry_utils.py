import itertools
import winreg
from typing import List, Union, Tuple, Any

import winerror


def set_reg_value(hkey: int, reg_path: str, reg_name: str, reg_value: Union[str, int], reg_type: int) -> None:
    with winreg.OpenKeyEx(hkey, reg_path, 0, winreg.KEY_SET_VALUE) as registry_key:
        winreg.SetValueEx(registry_key, reg_name, 0, reg_type, reg_value)


def get_reg_values(hkey: int, reg_path: str) -> List[Tuple[Any, Any, int]]:
    with winreg.OpenKeyEx(hkey, reg_path, 0, winreg.KEY_READ) as reg_key:
        values = []
        for index in itertools.count(start=0, step=1):
            try:
                value = winreg.EnumValue(reg_key, index)
                values.append(value)
            except WindowsError as e:
                if e.winerror == winerror.ERROR_NO_MORE_ITEMS:
                    break
                raise

    if not values:
        raise Exception(f"No values found for key {reg_path}")

    return values
