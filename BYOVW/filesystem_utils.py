import filecmp
import hashlib
import os
from typing import Union, List


def list_files_by_extensions(dir_path: str, extensions: Union[List[str], str]) -> List[str]:
    if isinstance(extensions, str):
        extensions = [extensions]

    dir_path_exp = os.path.expandvars(dir_path)
    dir_entries = os.scandir(dir_path_exp)
    files = []
    for dir_entry in dir_entries:
        if dir_entry.is_file():
            full_file_name = dir_entry.name
            file_name, file_extension = os.path.splitext(full_file_name)
            if file_extension in extensions:
                files.append(full_file_name)

    if not files:
        raise Exception(f"Did not find files with extensions {extensions} in directory: {dir_path_exp}")

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


def path_exists(file_path: str) -> bool:
    file_path_exp = os.path.expandvars(file_path)
    return os.path.exists(file_path_exp)


def is_file_contents_equal(file_path_1: str, file_path_2: str) -> bool:
    file_path_1_exp = os.path.expandvars(file_path_1)
    file_path_2_exp = os.path.expandvars(file_path_2)
    return filecmp.cmp(file_path_1_exp, file_path_2_exp)
