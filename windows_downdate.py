import logging
from dataclasses import dataclass
from typing import List

from utils.filesystem import is_path_exists, Path
from utils.xml_utils import load_xml, find_child_elements_by_match, get_element_attribute

logger = logging.getLogger(__name__)


CONFIG_XML_PATH = "resources/Config.xml"
PENDING_XML_PATH = "resources/Pending.xml"
DOWNGRADE_XML_PATH = "resources/Downgrade.xml"


@dataclass
class UpdateFile:

    source: Path
    destination: Path
    should_retrieve_oldest: bool
    is_oldest_retrieved: bool

    def to_hardlink_dict(self):
        return {"source": self.source.nt_path, "destination": self.destination.nt_path}


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


def main() -> None:
    parse_args()
    init_logger()
    update_files = parse_config_xml()


if __name__ == '__main__':
    main()
