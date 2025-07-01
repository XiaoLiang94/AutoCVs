# AutoCVs

## Automated CV measurements under various experimental conditions 

# Description
This code is for conducting the automated cyclic voltammetry (CV) measurements with real-time adjustments of various experimental conditions, including temperature, electrolyte composition, concentration, and flow rate. The code also has the functions, including in-situ electrode cleaning and removal of bubbles generated during the measurements, to address challenges encountered in the high-througput electrochemical measurements. 

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

# A reference schematic of the tube layout of the system
This schematic is to suggest the tube layout design of the system to the hardware developers.

<p align="center">
    <img src="https://github.com/user-attachments/assets/69c5bd18-5493-4129-8a13-36c8a747263c" alt="Volume Area" width="600"/>
</p>

# A schematic of the automated workflow
This schematic of the automated workflow is to help software developers to understand the code logic.

<p align="center">
    <img src="https://github.com/user-attachments/assets/cc89f02f-373e-4ac4-9a5d-b6bdd2eb5c94" alt="Volume Area" width="900"/>
</p>


# Details
### Folders
**Main code**: A Python script for automated CV tests at various Temperatures

## Authors

| **AUTHORS** |Xiao Liang            |
|-------------|----------------------|
| **VERSION** | 1.0 / July,2025                               |
| **EMAILS**  | xliang3@ic.ac.uk                         |
