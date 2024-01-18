from component_store import create_base_update_files

"""
Potential issues:
Some file elements do not contain destinationPath, usually .NET stuff
What about PA19 deltas? Would the MsDelta API handle it correctly? 
"""


def main():
    create_base_update_files()

    # Take care of XML identifier

    # Write pending

    # Make system un-updatable

    # Trigger update


if __name__ == '__main__':
    main()
