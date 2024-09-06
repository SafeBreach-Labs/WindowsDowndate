# Windows Downdate
<div align="center">
<img src="./images/Windows-Downdate-Logo.png" width="15%"/>
</div align="center">

## Overview
A tool that takes over Windows Updates to craft custom downgrades and expose past fixed vulnerabilities. Presented at Black Hat USA 2024 Briefings and DEFCON 32 under the title "Windows Downdate: Downgrade Attacks Using Windows Updates". [[**1**]](https://www.blackhat.com/us-24/briefings/schedule/#windows-downdate-downgrade-attacks-using-windows-updates-38963)[[**2**]](https://defcon.org/html/defcon-32/dc-32-speakers.html#54522)

Using Windows Downdate you can downgrade critical OS components, DLLs, Drivers, the NT kernel, the Secure Kernel, the Hyper-V hypervisor, Credential Guard and much more!

## Installation
To install Windows Downdate, follow the steps below.
1. Clone this repository
2. Change directory to the cloned repository directory
3. Run the following command (tested with python 3.11.9)
    ```
    pip install -r requirements.txt
    ```
4. You can now execute Windows Downdate


## Release Binary
Windows Downdate also supports PyInstaller pre-compiled binary that you can download [here](https://github.com/0xDeku/Windows-Downdate/releases)

## Usage
Windows Downdate operates on a config XML file that specifies the files to downgrade
```
windows_downdate.py --config-xml <CONFIG XML PATH> <ADDITIONAL ARGS>
```


### Config XML  Format

```xml
<Configuration>
    <UpdateFilesList>
        <UpdateFile source="path\to\source.exe" destination="path\to\destination.exe" />
    </UpdateFilesList>
</Configuration>
```

`<Configuration>`: The root element that encapsulates the entire configuration.

`<UpdateFilesList>`: A container element that holds one or more <UpdateFile> elements.

`<UpdateFile>`: Defines a single file downgrade operation.

`source`: The path of the downgrade source file. **Note that if the source file does not exist, Windows Downdate attempts to retrieve its base version from the component store.**

`destination`: The path of the downgrade destination file.

**Simply put** - take the XML snippet and insert `<UpdateFile>` elements, the `source` replaces the `destination`.

You can also refer to the [**examples**](./examples) directory as reference for finalized config XML files.

## Execution Options
Windows Downdate supports two execution options. 
### 1. Custom Downgrades
Windows Downdate supports crafting custom downgrades. 
To craft custom downgrade, you need to create a config XML file and just feed the tool with this config XML. 

### 2. Downgrade Usage Examples
Windows Downdate has built-in usage examples with ready config XML files and vulnerable modules. The supported usage examples are listed below.

1. [**CVE-2021-27090 Secure Kernel Elevation of Privilege Patch Downgrade**](./examples/CVE-2021-27090-Secure-Kernel-EoP-Patch-Downgrade)
2. [**CVE-2022-34709 Credential Guard Elevation of Privilege Patch Downgrade**](./examples/CVE-2022-34709-Credential-Guard-EoP-Patch-Downgrade)
3. [**CVE-2023-21768 AFD Driver Elevation of Privilege Patch Downgrade**](./examples/CVE-2023-21768-AFD-Driver-EoP-Patch-Downgrade)
4. [**Hyper-V Hypervisor Downgrade**](./examples/Hyper-V-Hypervisor-Downgrade)
5. [**Kernel Suite Downgrade**](./examples/Kernel-Suite-Downgrade)
6. [**PPLFault Patch Downgrade**](./examples/PPLFault-Patch-Downgrade)
7. [**VBS UEFI Lock Bypass**](./examples/VBS-UEFI-Locks-Bypass)

## Further Research
Do you have in mind any Windows components that may be vulnerable to downgrades? Use Windows Downdate for further research and to find additional vulnerabilities!

## Author - Alon Leviev
* LinkedIn - [Alon Leviev](https://il.linkedin.com/in/alonleviev)
* Twitter - [@_0xDeku](https://twitter.com/_0xDeku)
