import filecmp
import os
from typing import Union, List, Any, TypeVar, Type, Self
from pathlib import WindowsPath

# TODO: Better define Path object integration with filesystem_utils.py APIs



class DirectoryNotFound(Exception):
    pass


class FileNotFound(Exception):
    pass


class PathEx(WindowsPath):

    TPathEx = TypeVar("TPathEx")

    def __new__(cls: Type[TPathEx], path: str, *args: Any, **kwargs: Any) -> TPathEx:
        expanded_path = os.path.expandvars(path)
        args = (expanded_path, ) + args
        self = cls._from_parts(args)
        return self

    @property
    def nt_path(self: Self) -> str:
        return f"\\??\\{str(self)}"

    @property
    def full_path(self: Self) -> str:
        return str(self)


def get_path_modification_time(path_obj: PathEx) -> float:
    return os.path.getmtime(path_obj.full_path)


def list_dirs(dir_path: str, oldest_to_newest: bool = False) -> List[PathEx]:
    dirs = []
    dir_path_exp = os.path.expandvars(dir_path)
    for dir_entry in os.scandir(dir_path_exp):
        if dir_entry.is_dir():
            path_obj = PathEx(dir_entry.path)
            dirs.append(path_obj)

    if not dirs:
        raise DirectoryNotFound(f"Did not find directories in directory: {dir_path_exp}")

    if oldest_to_newest:
        dirs.sort(key=get_path_modification_time)

    return dirs


def list_files(dir_path: str) -> List[PathEx]:
    files = []
    dir_path_exp = os.path.expandvars(dir_path)
    for dir_entry in os.scandir(dir_path_exp):
        if dir_entry.is_file():
            path_obj = PathEx(dir_entry.path)
            files.append(path_obj)

    if not files:
        raise FileNotFound(f"Did not find files in directory: {dir_path_exp}")

    return files


def is_file_suits_extensions(file: str, extensions: Union[List[str], str]) -> bool:
    if isinstance(extensions, str):
        extensions = [extensions]

    _, file_extension = os.path.splitext(file)
    return file_extension in extensions


# TODO: Implement reading in chunks to avoid memory waste
def read_file(file_path: str, mode: str = "rb") -> Union[bytes, str]:
    file_path_exp = os.path.expandvars(file_path)
    with open(file_path_exp, mode) as f:
        return f.read()


def write_file(file_path: str, content: Union[str, bytes], mode: str = "wb") -> None:
    file_path_exp = os.path.expandvars(file_path)
    with open(file_path_exp, mode) as f:
        f.write(content)


def is_path_exists(file_path: str) -> bool:
    file_path_exp = os.path.expandvars(file_path)
    return os.path.exists(file_path_exp)


def is_file_contents_equal(file_path_1: str, file_path_2: str) -> bool:
    file_path_1_exp = os.path.expandvars(file_path_1)
    file_path_2_exp = os.path.expandvars(file_path_2)
    return filecmp.cmp(file_path_1_exp, file_path_2_exp)

