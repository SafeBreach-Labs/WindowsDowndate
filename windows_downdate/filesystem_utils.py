import filecmp
import os
from typing import Union, List, Any, TypeVar, Type, Self
from pathlib import WindowsPath


class PathEx(WindowsPath):
    """
    Extended WindowsPath class that supports NT path
    """

    TPathEx = TypeVar("TPathEx")

    # TODO: Add docs
    def __new__(cls: Type[TPathEx], path: str, *args: Any, **kwargs: Any) -> TPathEx:
        expanded_path = os.path.expandvars(path)
        args = (expanded_path, ) + args
        self = cls._from_parts(args)
        return self

    @property
    def nt_path(self: Self) -> str:
        """
        :return: The NT path as string
        """
        return f"\\??\\{self.full_path}"

    @property
    def full_path(self: Self) -> str:
        """
        :return: The full path as string
        """
        return str(self)


def get_path_modification_time(path_obj: PathEx) -> float:
    """
    Gets a path's last modification time

    :param path_obj: Initialized PathEx object to get its modification time
    :return: Path's last modification time as float
    """
    return os.path.getmtime(path_obj.full_path)


def list_dirs(dir_path: str, oldest_to_newest: bool = False) -> List[PathEx]:
    """
    Lists directories of a given path

    :param dir_path: The path of the directory to list its directories
    :param oldest_to_newest: Boolean stating if old to new sort is needed.
                             True for old to new sorting, False otherwise
    :return: List of initialized PathEx objects representing directories of dir_path
    :raises: Exception - if no directories are found in dir_path
    """
    dirs = []
    dir_path_exp = os.path.expandvars(dir_path)
    for dir_entry in os.scandir(dir_path_exp):
        if dir_entry.is_dir():
            path_obj = PathEx(dir_entry.path)
            dirs.append(path_obj)

    if not dirs:
        raise Exception(f"Did not find directories in directory: {dir_path_exp}")

    if oldest_to_newest:
        dirs.sort(key=get_path_modification_time)

    return dirs


def read_file(file_path: str, mode: str = "rb") -> Union[bytes, str]:
    """
    Reads a specified file

    :param file_path: Path to the file to read. Supports environment variables
    :param mode: The read mode
    :return: File content as bytes or string depending on the mode used
    """
    file_path_exp = os.path.expandvars(file_path)
    with open(file_path_exp, mode) as f:
        return f.read()


def write_file(file_path: str, content: Union[str, bytes], mode: str = "wb") -> None:
    """
    Writes content to a file

    :param file_path: Path to the file to write to. Supports environment variables
    :param content: The content to write to the file, bytes or string depending on the mode used
    :param mode: The write mode
    :return: None
    """
    file_path_exp = os.path.expandvars(file_path)
    with open(file_path_exp, mode) as f:
        f.write(content)


def is_path_exists(file_path: str) -> bool:
    """
    Check if file exists

    :param file_path: File path to check if exists. Supports environment variables
    :return: True if file exists, False otherwise
    """
    file_path_exp = os.path.expandvars(file_path)
    return os.path.exists(file_path_exp)


def is_file_contents_equal(file_path_1: str, file_path_2: str) -> bool:
    """
    Check if two files contents are equal

    :param file_path_1: Path of the first file. Supports environment variables
    :param file_path_2: Path of the first file. Supports environment variables
    :return: True if contents equal, False otherwise
    """
    file_path_1_exp = os.path.expandvars(file_path_1)
    file_path_2_exp = os.path.expandvars(file_path_2)
    return filecmp.cmp(file_path_1_exp, file_path_2_exp)
