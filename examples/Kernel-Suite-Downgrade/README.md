# Kernel Suite Downgrade

This usage example downgrades the Windows Kernel, the NTFS driver and the Filter Manager driver to their base versions. It exposes all vulnerabilities fixed in these components in Windows 22h2 and 23h2.

## Execution Steps
1. Install Windows Downdate as instructed [**here**](../../README.md)
2. Run the following command from the base repository directory
    ```
    windows_downdate.py --config-xml examples/Kernel-Suite-Downgrade/Config.xml
    ```

## Tested Versions
This usage example was tested against Windows 11 23h2 (22631.3810)
