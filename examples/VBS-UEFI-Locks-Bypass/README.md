# VBS UEFI Locks Bypass

This usage example invalidates the Secure Kernel powering VBS. This causes VBS to not load even if enforced with UEFI locks. Remote disablement of VBS should not be possible without physical access to the target machine.

## Execution Steps
1. Install Windows Downdate as instructed [**here**](../../README.md)
2. Run the following command from the base repository directory
    ```
    windows_downdate.py --config-xml examples/VBS-UEFI-Locks-Bypass/Config.xml
    ```

## Tested Versions
This usage example was tested against Windows 11 23h2 (22631.3810)

## Mitigations
There is a registry key that once set mitigates the bypass. 

```
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" /v Mandatory /t REG_DWORD /d 1 /f
``` 

There are multiple pitfalls to this key - 
1. It is not documented, and the consequences of using it are unknown
2. It is not added automatically when enabling UEFI lock for VBS, so VBS is by-default vulnerable

**Update October 2024: The "Mandatory" setting was documented by Microsoft and can be found [here](https://learn.microsoft.com/en-us/windows/security/hardware-security/enable-virtualization-based-protection-of-code-integrity)**
