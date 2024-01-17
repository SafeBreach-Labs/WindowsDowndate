import itertools
import winreg
from typing import List

import winerror


def get_reg_sub_keys(hkey: int, reg_path: str) -> List[str]:
    with winreg.OpenKeyEx(hkey, reg_path, 0, winreg.KEY_READ) as registry_key:
        sub_keys = []
        for index in itertools.count(start=0, step=1):
            try:
                sub_key = winreg.EnumKey(registry_key, index)
                sub_keys.append(sub_key)
            except WindowsError as e:
                if e.winerror == winerror.ERROR_NO_MORE_ITEMS:
                    break
                raise

    return sub_keys


def get_reg_value(hkey: int, reg_path: str, reg_name: str) -> str:
    with winreg.OpenKeyEx(hkey, reg_path, 0, winreg.KEY_QUERY_VALUE) as registry_key:
        value, _ = winreg.QueryValueEx(registry_key, reg_name)
    return value
