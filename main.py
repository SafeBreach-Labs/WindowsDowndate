import argparse
import logging
import os
import shutil
import sys
import time
from typing import List, Dict, Self

from windows_downdate.component_store_utils import get_components
from windows_downdate.filesystem_utils import PathEx, is_file_contents_equal, is_path_exists, read_file, write_file
from windows_downdate.manifest_utils import Manifest
from windows_downdate.privilege_utils import is_administrator
from windows_downdate.system_utils import restart_system
from windows_downdate.update_utils import pend_update, get_empty_pending_xml
from windows_downdate.wrappers.ms_delta import apply_delta, DELTA_FLAG_NONE
from windows_downdate.xml_utils import load_xml, find_child_elements_by_match, get_element_attribute, create_element, \
    append_child_element


logger = logging.getLogger(__name__)


class UpdateFile:
    """
    Represents an update file
    """

    def __init__(self: Self, source_path: str, destination_path: str) -> None:
        """
        Initializes instance fields

        :param source_path: The path of the source file, will replace destination_path.
                            If the path does not exist, it will be marked for retrieval from the component store
        :param destination_path: The path of the destination file, will be replaced by source_path.
                                 This path mush exist
        :raises: Exception - if the destination file does not exist
        :return: None
        """
        self._source_path_obj = PathEx(source_path)
        self._destination_path_obj = PathEx(destination_path)
        self._should_retrieve_oldest = False
        self._is_oldest_retrieved = False
        self._skip_update = False

        if not self._destination_path_obj.exists():
            raise FileNotFoundError(f"The file to update {self._destination_path_obj.full_path} does not exist")

        if not self._source_path_obj.exists():
            self._should_retrieve_oldest = True
        else:
            self._verify_source_and_destination_equality()

    def verify_no_errors_or_raise(self: Self) -> None:
        """
        Verify that oldest file retrieved if it should have been

        :raises: Exception - if oldest destination file retrieval failed
        :return: None
        """
        if self._should_retrieve_oldest and not self._is_oldest_retrieved:
            raise Exception("Oldest destination file retrieval failed. "
                            f"Destination {self._destination_path_obj.name} may not be part of the component store")

    def _is_src_and_dst_equal(self: Self) -> bool:
        """
        Check if source and destination files equal

        :return: True if files are equal, False otherwise
        """
        return is_file_contents_equal(self._source_path_obj.full_path, self._destination_path_obj.full_path)

    def to_hardlink_dict(self: Self) -> Dict[str, str]:
        """
        Creates the HardlinkFile dict to be used in the Pending.xml action list

        :return: Dict in the following format - source: source NT path, destination: destionation NT path
        """
        return {"source": self._source_path_obj.nt_path, "destination": self._destination_path_obj.nt_path}

    def retrieve_oldest_source_file_from_sxs(self: Self, source_sxs_path: str) -> None:
        """
        Retrieves the oldest source file exists in the component store and writes it to the source path

        :param source_sxs_path: The path to the source file store in the component store
        :return: None
        :note: This method assumes the source is a component store file
        """
        self._create_source_directory_tree()
        self._apply_reverse_diff_or_copy(source_sxs_path)
        self._verify_source_and_destination_equality()

    def _create_source_directory_tree(self: Self) -> None:
        """
        Creates the source path if does not exist

        :return: None
        """
        os.makedirs(self._source_path_obj.parent, exist_ok=True)

    def _apply_reverse_diff_or_copy(self: Self, source_sxs_path: str) -> None:
        """
        If the store is diff type, applies the reverse diff to get the base file
        Otherwise, if store is not diff type, the file in the store is the oldest file available

        :param source_sxs_path: The path to the source file store in the component store
        :return: None
        """
        updated_file_path = f"{source_sxs_path}\\{self._destination_path_obj.name}"
        reverse_diff_file_path = f"{source_sxs_path}\\r\\{self._destination_path_obj.name}"

        # If there is reverse diff, apply it to create the base file
        if is_path_exists(reverse_diff_file_path):
            updated_file_content = read_file(updated_file_path)
            reverse_diff_file_content = read_file(reverse_diff_file_path)[4:]  # Remove CRC checksum
            base_content = apply_delta(DELTA_FLAG_NONE, updated_file_content, reverse_diff_file_content)
            write_file(self._source_path_obj.full_path, base_content)

        # If there is no reverse diff, the update file is the oldest file available
        else:
            shutil.copyfile(updated_file_path, self._source_path_obj.full_path)

        self._is_oldest_retrieved = True
        logger.info(f"Retrieved oldest destination file for {self._destination_path_obj.name}")

    def _verify_source_and_destination_equality(self: Self) -> None:
        """
        Verifies that source and destination are not equal. If equal, marks update file to be skipped

        :return: None
        """
        if self._is_src_and_dst_equal():
            self._skip_update = True
            logger.info(f"Will skip update of {self.destination_path_obj.name}, source and destination equal")

    @property
    def source_path_obj(self: Self) -> PathEx:
        """
        :return: The source's PathEx object
        """
        return self._source_path_obj

    @property
    def destination_path_obj(self: Self) -> PathEx:
        """
        :return: The destination's PathEx object
        """
        return self._destination_path_obj

    @property
    def should_retrieve_oldest(self: Self) -> bool:
        """
        :return: Boolean stating if oldest file retrival is needed
        """
        return self._should_retrieve_oldest

    @property
    def is_oldest_retrieved(self: Self) -> bool:
        """
        :return: Boolean stating if oldest file was retrieved
        """
        return self._is_oldest_retrieved

    @property
    def skip_update(self: Self) -> bool:
        """
        :return: Boolean stating if update should be skipped on this file
        """
        return self._skip_update


def parse_args() -> argparse.Namespace:
    """
    Parses command line arguments passed to this program

    :return: Parsed command line arguments as argparse.Namespace object
    """
    parser = argparse.ArgumentParser(description="Windows-Downdate: Craft any customized Windows Update")
    parser.add_argument("--config-xml", type=str, required=True, help="Path to the Config.xml file.")
    parser.add_argument("--force-restart", action="store_true", required="--restart-timeout" in sys.argv,
                        help="Flag specifying whether to force an automatic machine restart. "
                             "Update takes place during the restart.")
    parser.add_argument("--restart-timeout", type=int, default=10,
                        help="How much time to wait until the automatic machine restart.")
    parser.add_argument("--elevate", action="store_true",
                        help="Flag specifying whether to elevate to TrustedInstaller. "
                             "Functionality is the same, but smoother with TrustedInstaller. "
                             "Not recommended if facing an EDR!")

    return parser.parse_args()


def init_logger() -> None:
    """
    Initializes the logger and formats it

    :return: None
    """
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    log_format = logging.Formatter('[%(levelname)s] %(message)s')
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)


def parse_config_xml(config_file_path: str) -> List[UpdateFile]:
    """
    Parses given config XML file to create a list of initialized UpdateFile objects

    :param config_file_path: The path to the Config XML file.
                             Does not support environment variables
    :raises: Exception - if no UpdateFile instances could be created from the config XML file
                         This will usually happen if the config XML format is incorrect
    :return: List of initialized UpdateFile objects
    """

    config_xml = load_xml(config_file_path)

    update_files = []
    for update_file in find_child_elements_by_match(config_xml, "./UpdateFilesList/UpdateFile"):
        destination_file = get_element_attribute(update_file, "destination")
        source_file = get_element_attribute(update_file, "source")
        update_file_obj = UpdateFile(source_file, destination_file)
        update_files.append(update_file_obj)

    if not update_files:
        raise Exception("Empty update files post config file parsing. Make sure to have a correct config file")

    return update_files


def retrieve_oldest_files_for_update_files(update_files: List[UpdateFile]) -> None:
    """
    Iterates over UpdateFile list and retrieves oldest files for specified UpdateFile's from the component store

    The retrieval algorithm is as follows:
        1. Iterate over each component in the component store, from old to new
        2. Check if the update file's oldest file should be retrieved, continue otherwise
        3. Check if update file is part of the iterated component, continue otherwise
        4. Retrieve the oldest file from the store

    :param update_files: List of initialized UpdateFile objects
    :return: None
    :note: There is no documented way to get all stores of given file.
           The way I do it is by iterating over all components from old to new
           Then I parse the store's manifest, and given the manifest I know which files are part of the store
    """
    logger.info(f"Starting oldest files retrieval... This may take some time")
    start_time = time.time()

    for component in get_components():
        manifest = Manifest(component.name)
        for update_file in update_files:
            if not update_file.should_retrieve_oldest or update_file.is_oldest_retrieved:
                continue

            # Make sure that the destination file is part of the iterated component
            if not manifest.is_file_in_manifest_files(update_file.destination_path_obj.full_path):
                continue

            update_file.retrieve_oldest_source_file_from_sxs(component.full_path)

    for update_file in update_files:
        update_file.verify_no_errors_or_raise()

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f"Finished oldest file retrieval. {elapsed_time} seconds taken")


def craft_downgrade_xml(update_files: List[UpdateFile], downgrade_xml_path: str) -> None:
    """
    Crafts the downgrading Pending XML file using initialized UpdateFile object list

    :param update_files: List of initialized UpdateFile objects
    :param downgrade_xml_path: The path where the downgrading Pending XML is written to.
                               Does not support environment variables
    :return: None
    """
    downgrade_xml = get_empty_pending_xml()
    poq_element = find_child_elements_by_match(downgrade_xml, "./POQ")[0]  # Post reboot POQ is always at index 0

    for update_file in update_files:
        if update_file.skip_update:
            continue

        hardlink_dict = update_file.to_hardlink_dict()
        hardlink_element = create_element("HardlinkFile", hardlink_dict)
        append_child_element(poq_element, hardlink_element)
        logger.info(f"{update_file.destination_path_obj.full_path} -> {update_file.source_path_obj.full_path}")

    downgrade_xml.write(downgrade_xml_path, xml_declaration=True, encoding="utf-8")
    logger.info(f"Written downgrade XML to disk: {downgrade_xml_path}")


def main() -> None:
    cwd = os.getcwd()
    os.environ["CWD"] = cwd
    init_logger()
    args = parse_args()

    logger.info("Starting Windows-Downdate")

    if not is_administrator():
        raise Exception("Windows-Downdate must be run as an Administrator")

    update_files = parse_config_xml(args.config_xml)
    logger.info("Parsed config file")

    retrieve_oldest_files_for_update_files(update_files)

    downgrade_xml_path = f"{cwd}\\Downgrade.xml"
    craft_downgrade_xml(update_files, downgrade_xml_path)

    pend_update(downgrade_xml_path, args.elevate)
    logger.info("Pended update with downgrade XML")

    if args.force_restart:
        restart_system(args.restart_timeout)
        logger.info(f"System restart in {args.restart_timeout}")
    else:
        logger.info("You must manually restart the system for the update to take effect")

    logger.info("Ending Windows-Downdate")


if __name__ == '__main__':
    main()
