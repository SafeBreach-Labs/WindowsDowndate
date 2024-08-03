import os
import winreg
from typing import List

import win32security

from windows_downdate.filesystem_utils import list_dirs, PathEx
from windows_downdate.privilege_utils import enable_privilege

COMPONENT_STORE_PATH = "%SystemRoot%\\WinSxS\\"

COMPONENT_DIR_PREFIXES = ["amd64", "msil", "wow64", "x86"]

COMPONENTS_HIVE_PATH = "%SystemRoot%\\System32\\Config\\COMPONENTS"


def is_component_dir(dir_name: str) -> bool:
    """
    Checks if the given directory is a component by comparing against a known component directory prefixes
    Prefixes are - amd64, msil, wow64, x86

    :param dir_name: The directory name to check
    :return: True if component directory, False otherwise
    :note: Check is case-insensitive
    """
    for prefix in COMPONENT_DIR_PREFIXES:
        if dir_name.lower().startswith(prefix.lower()):
            return True

    return False


def get_components() -> List[PathEx]:
    """
    Gets list of all components in the store from old to new

    :return: List of initialized PathEx objects, each represents a component directory
    :raises: Exception - if did not find component directories in the component store
    """
    components = []
    for component_store_dir in list_dirs(COMPONENT_STORE_PATH, oldest_to_newest=True):
        if is_component_dir(component_store_dir.name):
            components.append(component_store_dir)

    if not components:
        raise Exception(f"Did not find component directories in component store")

    return components


def load_components_hive() -> None:
    """
    Loads the COMPONENTS hive from %SystemRoot%\System32\Config\COMPONENTS

    :return: None
    """
    # Make sure the required privileges for loading the hive are held
    enable_privilege(win32security.SE_BACKUP_NAME)
    enable_privilege(win32security.SE_RESTORE_NAME)

    components_hive_path_exp = os.path.expandvars(COMPONENTS_HIVE_PATH)
    winreg.LoadKey(winreg.HKEY_LOCAL_MACHINE, "COMPONENTS", components_hive_path_exp)
