import filecmp
import os
from typing import Union, List


# TODO: Better define Path object integration with filesystem.py APIs


class DirectoryNotFound(Exception):
    pass


class FileNotFound(Exception):
    pass


class Path:

    def __init__(self, full_path: str) -> None:
        self.full_path = os.path.expandvars(full_path)
        self.parent_dir = os.path.dirname(self.full_path)
        self.name = os.path.basename(self.full_path)
        self.nt_path = os.path.normpath(fr"\??\{self.full_path}")

    def __eq__(self, other) -> bool:
        return self.name == other


def get_path_modification_time(path_obj: Path) -> float:
    return os.path.getmtime(path_obj.full_path)


def list_dirs(dir_path: str, oldest_to_newest: bool = False) -> List[Path]:
    dirs = []
    dir_path_exp = os.path.expandvars(dir_path)
    for dir_entry in os.scandir(dir_path_exp):
        if dir_entry.is_dir():
            path_obj = Path(dir_entry.path)
            dirs.append(path_obj)

    if not dirs:
        raise DirectoryNotFound(f"Did not find directories in directory: {dir_path_exp}")

    if oldest_to_newest:
        dirs.sort(key=get_path_modification_time)

    return dirs


def list_files(dir_path: str) -> List[Path]:
    files = []
    dir_path_exp = os.path.expandvars(dir_path)
    for dir_entry in os.scandir(dir_path_exp):
        if dir_entry.is_file():
            path_obj = Path(dir_entry.path)
            files.append(path_obj)

    if not files:
        raise FileNotFound(f"Did not find files in directory: {dir_path_exp}")

    return files


def is_file_suits_extensions(file: str, extensions: Union[List[str], str]) -> bool:
    if isinstance(extensions, str):
        extensions = [extensions]

    file_name, file_extension = os.path.splitext(file)
    return file_extension in extensions

    
def list_files_by_extensions(dir_path: str, extensions: Union[List[str], str]) -> List[Path]:
    files = []
    for file in list_files(dir_path):
        if is_file_suits_extensions(file.name, extensions):
            files.append(file)

    if not files:
        raise Exception(f"Did not find files with extensions {extensions} in directory: {dir_path}")

    return files


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


def create_dir(dir_path: str, exist_ok: bool = False):
    dir_path_exp = os.path.expandvars(dir_path)
    try:
        os.mkdir(dir_path_exp)
    except FileExistsError:
        if not exist_ok:
            raise
