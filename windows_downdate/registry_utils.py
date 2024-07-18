import itertools
import winreg
from typing import List, Union, Tuple, Any

import winerror


def get_reg_sub_keys(hkey: int, reg_path: str) -> List[str]:
    with winreg.OpenKeyEx(hkey, reg_path, 0, winreg.KEY_READ) as reg_key:
        sub_keys = []
        for index in itertools.count(start=0, step=1):
            try:
                sub_key = winreg.EnumKey(reg_key, index)
                sub_keys.append(sub_key)
            except WindowsError as e:
                if e.winerror == winerror.ERROR_NO_MORE_ITEMS:
                    break
                raise

    if not sub_keys:
        raise Exception(f"No sub keys found for key {reg_path}")

    return sub_keys


def get_reg_value(hkey: int, reg_path: str, reg_name: str) -> str:
    with winreg.OpenKeyEx(hkey, reg_path, 0, winreg.KEY_QUERY_VALUE) as registry_key:
        value, _ = winreg.QueryValueEx(registry_key, reg_name)
    return value


def set_reg_value(hkey: int, reg_path: str, reg_name: str, reg_value: Union[str, int], reg_type: int) -> None:
    with winreg.OpenKeyEx(hkey, reg_path, 0, winreg.KEY_SET_VALUE) as registry_key:
        winreg.SetValueEx(registry_key, reg_name, 0, reg_type, reg_value)


# TODO: This code is similar to get_reg_sub_keys, consider merging
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
