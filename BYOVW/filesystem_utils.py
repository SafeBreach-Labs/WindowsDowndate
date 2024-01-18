import filecmp
import os
from typing import Union, List


class DirectoryNotFound(Exception):
    pass


class FileNotFound(Exception):
    pass


def list_dirs(dir_path: str, return_name_only: bool = False, oldest_to_newest: bool = False) -> List[str]:
    dirs = []
    dir_path_exp = os.path.expandvars(dir_path)
    for dir_entry in os.scandir(dir_path_exp):
        if dir_entry.is_dir():
            dirs.append(dir_entry.path)

    if not dirs:
        raise DirectoryNotFound(f"Did not find directories in directory: {dir_path_exp}")

    if oldest_to_newest:
        dirs.sort(key=os.path.getmtime)

    if return_name_only:
        dirs = [os.path.basename(dir) for dir in dirs]

    return dirs


def list_files(dir_path: str, return_name_only: bool = False) -> List[str]:
    files = []
    dir_path_exp = os.path.expandvars(dir_path)
    for dir_entry in os.scandir(dir_path_exp):
        if dir_entry.is_file():
            files.append(dir_entry.name if return_name_only else dir_entry.path)

    if not files:
        raise FileNotFound(f"Did not find files in directory: {dir_path_exp}")

    return files


def is_file_suits_extensions(file: str, extensions: Union[List[str], str]) -> bool:
    if isinstance(extensions, str):
        extensions = [extensions]

    file_name, file_extension = os.path.splitext(file)
    return file_extension in extensions

    
def list_files_by_extensions(dir_path: str, extensions: Union[List[str], str]) -> List[str]:
    files = []
    for file in list_files(dir_path, return_name_only=True):
        if is_file_suits_extensions(file, extensions):
            files.append(file)

    if not files:
        raise Exception(f"Did not find files with extensions {extensions} in directory: {dir_path}")

    return files


# TODO: Implement reading in chunks to avoid memory waste
def read_file(file_path: str, mode: str = "rb") -> Union[bytes, str]:
    file_path_exp = os.path.expandvars(file_path)
    with open(file_path_exp, mode) as f:
        return f.read()


def write_file(file_path: str, content: Union[str, bytes], mode: str = "wb"):
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
