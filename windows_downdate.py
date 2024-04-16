import logging

from utils.filesystem import is_path_exists, Path
from utils.xml_utils import load_xml, find_child_elements_by_match, get_element_attribute, create_element, \
    append_child_element
from utils.component_store import retrieve_oldest_file_by_file_path

logger = logging.getLogger(__name__)


CONFIG_FILE_PATH = "resources/Config.xml"
PENDING_XML_PATH = "resources/Pending.xml"
DOWNGRADE_XML_PATH = "resources/Downgrade.xml"


def init_logger() -> None:
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    log_format = logging.Formatter('[%(levelname)s]: %(message)s')
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)


def parse_config_xml() -> None:

    pending_xml = load_xml(PENDING_XML_PATH)
    poq_element = find_child_elements_by_match(pending_xml, "./POQ")[0]  # Post reboot POQ is always at index 0

    config_xml = load_xml(CONFIG_FILE_PATH)

    for update_file in find_child_elements_by_match(config_xml, "./UpdateFilesList/UpdateFile"):
        source_file = get_element_attribute(update_file, "source")
        source_file_obj = Path(source_file)
        destination_file = get_element_attribute(update_file, "destination")
        destination_file_obj = Path(destination_file)

        # If the destination does not exist, we can not update it
        if not is_path_exists(destination_file_obj.full_path):
            raise FileNotFoundError(f"The file to update {destination_file_obj.full_path} does not exist")

        # If the source does not exist, retrieve its oldest version from the component store
        if not is_path_exists(source_file_obj.full_path):
            retrieve_oldest_file_by_file_path(destination_file_obj, source_file_obj)

        hardlink_dict = {"source": source_file_obj.nt_path, "destination": destination_file_obj.nt_path}
        hardlink_element = create_element("HardlinkFile", hardlink_dict)
        append_child_element(poq_element, hardlink_element)

    pending_xml.write(DOWNGRADE_XML_PATH)


def parse_args() -> None:
    pass


def main() -> None:
    init_logger()
    parse_config_xml()


if __name__ == '__main__':
    main()
