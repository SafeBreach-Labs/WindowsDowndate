import os
import shutil
import time
from typing import List

from windows_downdate import UpdateFile
from windows_downdate.filesystem_utils import read_file, list_dirs, is_path_exists, write_file, Path
from windows_downdate.manifest_utils import Manifest
from windows_downdate.wrappers.ms_delta import apply_delta, DELTA_FLAG_NONE


COMPONENT_STORE_PATH = "%SystemRoot%\\WinSxS\\"

COMPONENT_DIR_PREFIXES = ["amd64", "msil", "wow64", "x86"]


def is_component_dir(dir_name: str, case_sensitive: bool = False) -> bool:
    for prefix in COMPONENT_DIR_PREFIXES:
        if not case_sensitive:
            dir_name = dir_name.lower()
            prefix = prefix.lower()

        return dir_name.startswith(prefix)


def get_components() -> List[Path]:
    components = []
    for component_store_dir in list_dirs(COMPONENT_STORE_PATH, oldest_to_newest=True):
        if is_component_dir(component_store_dir.name):
            components.append(component_store_dir)

    if not components:
        raise Exception(f"Did not find component directories in component store")

    return components


# TODO: Update file related function, so should not reside here
def retrieve_oldest_files_for_update_files(update_files: List[UpdateFile]) -> None:
    print(f"Starting oldest files retrieval... This may take some time")
    start_time = time.time()

    for component in get_components():
        manifest = Manifest(component.name)
        for update_file in update_files:
            if not update_file.should_retrieve_oldest or update_file.is_oldest_retrieved:
                continue

            if not manifest.is_file_in_manifest_files(update_file.destination_path_obj.full_path):
                continue

            # Create the directory tree of the update file source
            os.makedirs(update_file.source_path_obj.parent_dir, exist_ok=True)

            updated_file_path = f"{component.full_path}\\{update_file.destination_path_obj.name}"
            reverse_diff_file_path = f"{component.full_path}\\r\\{update_file.destination_path_obj.name}"

            # If there is reverse diff, apply it to create the base file
            if is_path_exists(reverse_diff_file_path):
                updated_file_content = read_file(updated_file_path)
                reverse_diff_file_content = read_file(reverse_diff_file_path)[4:]  # Remove CRC checksum
                base_delta_output_obj = apply_delta(DELTA_FLAG_NONE, updated_file_content, reverse_diff_file_content)
                base_content = base_delta_output_obj.get_buffer()
                write_file(update_file.source_path_obj.full_path, base_content)

            # If there is no reverse diff, the update file is the oldest file available
            else:
                shutil.copyfile(updated_file_path, update_file.source_path_obj.full_path)

            update_file.is_oldest_retrieved = True
            print(f"Retrieved oldest destination file for {update_file.destination_path_obj.name}")

    for update_file in update_files:
        if update_file.should_retrieve_oldest and not update_file.is_oldest_retrieved:
            raise Exception("Oldest destination file retrieval failed. "
                            f"Destination {update_file.destination_path_obj.name} is not part of the component store")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Finished oldest file retrieval. {elapsed_time} seconds taken")
