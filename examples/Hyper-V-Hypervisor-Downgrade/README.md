# Hyper-V Hypervisor Downgrade

This usage example downgrades the Hyper-V hypervisor to a two-year-old version.

## Execution Steps
1. Install Windows Downdate as instructed [**here**](../../README.md)
2. Run the following command from the base repository directory
    ```
    windows_downdate.py --config-xml examples/Hyper-V-Hypervisor-Downgrade/Config.xml
    ```

## Issued CVE-2024-21302
This usage example was reported to Microsoft and [CVE-2024-21302](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-21302) was issued.

## Tested Versions
This usage example was tested against Windows 11 23h2 (22631.3810)
