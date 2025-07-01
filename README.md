# AutoCVs

## Automated CV measurements under various experimental conditions 

# Description
This code is for conducting the automated cyclic voltammetry (CV) measurements with real-time adjustments of various experimental conditions, including temperature, electrolyte composition, concentration, and flow rate. The code also includes the functions, including in-situ electrode cleaning and removal of bubbles generated during the measurements, to address challenges encountered in the high-througput electrochemical measurements. 

A Python script for demonstrating the automated CV measurements at various temperatures is attached. The settings for other experimental conditions can be directly modified in the script as needed for the experiment.

# Hardware devices
* Four pressure pumps (Flow EZ™, Fluigent)
* Four flow rate sensors (FLU-M+, Fluigent)
* A multi-switch valve (M-SWITCH™, Fluigent)
* A 2-switch valve (2-SWITCH™, Fluigent)
* An electrochemical workstation (CHI 660E, CH Instruments)
* A CMOS camera (MS-XG903GC/M, Minsvison)
* A water bath (ARCTIC A10 with a SC150 controller, Thermo Scientific)

# Python packages required for device control
* Fluigent.SDK (for Fluigent devices control)
* hardpotato (for CHI electrochemical workstation control)
* mvsdk (for Minsvison camera control)

# A schematic of the automated workflow
This schematic of the automated workflow is to help developers to understand the code logic.

![image](https://private-user-images.githubusercontent.com/149203429/461213313-cc89f02f-373e-4ac4-9a5d-b6bdd2eb5c94.png?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTEzOTc5MDUsIm5iZiI6MTc1MTM5NzYwNSwicGF0aCI6Ii8xNDkyMDM0MjkvNDYxMjEzMzEzLWNjODlmMDJmLTM3M2UtNGFjNC05YTVkLWI2YmRkMmViNWM5NC5wbmc_WC1BbXotQWxnb3JpdGhtPUFXUzQtSE1BQy1TSEEyNTYmWC1BbXotQ3JlZGVudGlhbD1BS0lBVkNPRFlMU0E1M1BRSzRaQSUyRjIwMjUwNzAxJTJGdXMtZWFzdC0xJTJGczMlMkZhd3M0X3JlcXVlc3QmWC1BbXotRGF0ZT0yMDI1MDcwMVQxOTIwMDVaJlgtQW16LUV4cGlyZXM9MzAwJlgtQW16LVNpZ25hdHVyZT0wMTBjNzBlZjg3YjQ5NDNkMjNjNDUxMDI3NWQwODg2ZTZkOGQ1NjY4ODBkZTI4M2I1MmZlOTRlMmQ0OWIyMTdmJlgtQW16LVNpZ25lZEhlYWRlcnM9aG9zdCJ9.yc24uWFtMpgI4dS78aFj2wSohRZb9fafEb8vUDaDHTs)

# Details
### Folders
**Main code**: A Python script for automated CV tests at various Temperatures

## Authors

| **AUTHORS** |Xiao Liang            |
|-------------|----------------------|
| **VERSION** | 1.0 / July,2025                               |
| **EMAILS**  | xliang3@ic.ac.uk                         |
