# ItsNotASecurityBoundary Patch Downgrade

This usage example downgrades the patch of [ItsNotASecurityBoundary](https://www.elastic.co/security-labs/false-file-immutability).


## Execution Steps
1. Install Windows Downdate as instructed [**here**](../../README.md)
2. Run the following command from the base repository directory
    ```
    windows_downdate.py --config-xml examples/ItsNotASecurityBoundary-Patch-Downgrade/Config.xml
    ```

## Tested Versions
This usage example was tested against Windows 11 23h2 (22631.4317)

## Credits
[Gabriel Landau](https://x.com/GabrielLandau)
