import itertools
import winreg
from typing import List, Union, Tuple, Any

import winerror


def set_reg_value(hkey: int, reg_path: str, reg_name: str, reg_value: Union[str, int], reg_type: int) -> None:
    """
    Sets registry value

    :param hkey: An already open key or one of winreg's hkey constants
    :param reg_path: The path of the registry
    :param reg_name: The name of the key to set its value
    :param reg_value: The value to set
    :param reg_type: The value type
    :return: None
    """
    with winreg.OpenKeyEx(hkey, reg_path, 0, winreg.KEY_SET_VALUE) as registry_key:
        winreg.SetValueEx(registry_key, reg_name, 0, reg_type, reg_value)


def get_reg_values(hkey: int, reg_path: str) -> List[Tuple[Any, Any, int]]:
    """
    Get registry values

    :param hkey: An already open key or one of winreg's hkey constants
    :param reg_path: The path of the registry the get its values
    :return: List of registry values. Value is a tuple in the following format - (key_name, key_value, value_type)
    :raises: Exception - if no values were found for reg_path
    """
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
