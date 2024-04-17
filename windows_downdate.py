import logging
from typing import List

from utils.component_store import retrieve_oldest_files_for_update_files, UpdateFile
from utils.filesystem import is_path_exists, Path, is_file_contents_equal
from utils.xml_utils import load_xml, find_child_elements_by_match, get_element_attribute, create_element, \
    append_child_element

logger = logging.getLogger(__name__)


CONFIG_XML_PATH = "resources\\Config.xml"
PENDING_XML_PATH = "resources\\Pending.xml"
DOWNGRADE_XML_PATH = "resources\\Downgrade.xml"


def parse_args() -> None:
    pass


def init_logger() -> None:
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    log_format = logging.Formatter('[%(levelname)s] %(message)s')
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)


def parse_config_xml() -> List[UpdateFile]:

    config_xml = load_xml(CONFIG_XML_PATH)

    update_files = []
    for update_file in find_child_elements_by_match(config_xml, "./UpdateFilesList/UpdateFile"):
        destination_file = get_element_attribute(update_file, "destination")
        destination_file_obj = Path(destination_file)

        # If the destination does not exist, we can not update it
        if not is_path_exists(destination_file_obj.full_path):
            raise FileNotFoundError(f"The file to update {destination_file_obj.full_path} does not exist")

        source_file = get_element_attribute(update_file, "source")
        source_file_obj = Path(source_file)

        # If the source does not exist, retrieve its oldest version from the component store
        if not is_path_exists(source_file_obj.full_path):
            should_retrieve_oldest = True
        else:
            should_retrieve_oldest = False

        update_file_obj = UpdateFile(source_file_obj, destination_file_obj, should_retrieve_oldest, False)
        update_files.append(update_file_obj)

    return update_files


def write_update_files_to_downgrade_xml(update_files: List[UpdateFile]) -> None:
    pending_xml = load_xml(PENDING_XML_PATH)
    poq_element = find_child_elements_by_match(pending_xml, "./POQ")[0]  # Post reboot POQ is always at index 0

    for update_file in update_files:

        # Let's make sure we do not update files that are the same
        if is_file_contents_equal(update_file.source.full_path, update_file.destination.full_path):
            logger.info(f"Skipping update of {update_file.destination.name}, source and destination are the same")
            continue

        hardlink_dict = update_file.to_hardlink_dict()
        hardlink_element = create_element("HardlinkFile", hardlink_dict)
        append_child_element(poq_element, hardlink_element)

    pending_xml.write(DOWNGRADE_XML_PATH)


def main() -> None:
    parse_args()
    init_logger()
    update_files = parse_config_xml()
    retrieve_oldest_files_for_update_files(update_files)
    write_update_files_to_downgrade_xml(update_files)


if __name__ == '__main__':
    main()
