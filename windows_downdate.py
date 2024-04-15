import logging
import os

logger = logging.getLogger(__name__)


CONFIG_FILE_PATH = "resources/Config.xml"


def init_logger() -> None:
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    log_format = logging.Formatter('[%(levelname)s]: %(message)s')
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)


def parse_config_file() -> None:
    if not os.path.exists(CONFIG_FILE_PATH):
        raise FileNotFoundError("Config file Config.xml does not exist")


def main() -> None:
    init_logger()

    parse_config_file()


if __name__ == '__main__':
    main()
