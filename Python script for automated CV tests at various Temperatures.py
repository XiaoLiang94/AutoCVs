# -*- coding: utf-8 -*-

from __future__ import print_function 
import time

# import Fluignet package, including Pumps, flow sensors, Valve.
from Fluigent.SDK import fgt_init, fgt_close
from Fluigent.SDK import fgt_set_pressure, fgt_set_sensorRegulation, fgt_set_sensorRegulationResponse
from Fluigent.SDK import fgt_get_sensorValue
from Fluigent.SDK import fgt_get_valveChannelCount
from Fluigent.SDK import fgt_get_valvePosition, fgt_set_valvePosition
fgt_init()

# import EC worksation package
import hardpotato as hp
import os

# import water bath package
import serial

# import camera package
import threading
import mvsdk



### Define fuctions ###--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# camera control function
class CameraRecorder:
    def __init__(self, max_recording_time, save_path):
        self.max_recording_time = max_recording_time  # Maximum recording time in seconds
        self.save_path = save_path  # Path where video will be saved

        # Enumerate cameras
        DevList = mvsdk.CameraEnumerateDevice()
        nDev = len(DevList)
        if nDev < 1:
            print("No camera was found!")
            return

        DevInfo = DevList[0]  # Automatically select the first camera
        print(DevInfo)

        # Open the camera
        self.hCamera = 0
        try:
            self.hCamera = mvsdk.CameraInit(DevInfo, -1, -1)
            mvsdk.CameraSetTriggerMode(self.hCamera, 1)
        except mvsdk.CameraException as e:
            print("CameraInit Failed({}): {}".format(e.error_code, e.message))
            return

        cap = mvsdk.CameraGetCapability(self.hCamera)
        monoCamera = (cap.sIspCapacity.bMonoSensor != 0)
        if monoCamera:
            mvsdk.CameraSetIspOutFormat(self.hCamera, mvsdk.CAMERA_MEDIA_TYPE_MONO8)

        # Set manual exposure time
        mvsdk.CameraSetAeState(self.hCamera, 0)
        mvsdk.CameraSetExposureTime(self.hCamera, 2 * 1000)

        mvsdk.CameraPlay(self.hCamera)

        FrameBufferSize = cap.sResolutionRange.iWidthMax * cap.sResolutionRange.iHeightMax * (1 if monoCamera else 3)
        self.pFrameBuffer = mvsdk.CameraAlignMalloc(FrameBufferSize, 16)

        # Initialize recording with the specified path
        self.ErrCode = mvsdk.CameraInitRecord(self.hCamera, 4, self.save_path, True, 100, 25)

    def start_recording(self):
        time.sleep(4)
        if self.ErrCode != 0:
            print("Failed to initialize recording.")
            return

        start_time = time.time()  # Get the start time
        print("Recording started...")

        while True:
            elapsed_time = time.time() - start_time  # Calculate elapsed time
            if elapsed_time > self.max_recording_time:  # Stop if max recording time is exceeded
                print(f"Max recording time of {self.max_recording_time} seconds reached.")
                break

            try:
                mvsdk.CameraSoftTrigger(self.hCamera)
                pRawData, FrameHead = mvsdk.CameraGetImageBuffer(self.hCamera, 2000)
                mvsdk.CameraImageProcess(self.hCamera, pRawData, self.pFrameBuffer, FrameHead)
                mvsdk.CameraReleaseImageBuffer(self.hCamera, pRawData)

                mvsdk.CameraPushFrame(self.hCamera, self.pFrameBuffer, FrameHead)

            except mvsdk.CameraException as e:
                print("CameraGetImageBuffer failed({}): {}".format(e.error_code, e.message))
                break

        # Cleanup after recording
        self.cleanup()

    def cleanup(self):
        print("Cleaning up camera resources...")
        mvsdk.CameraStopRecord(self.hCamera)
        mvsdk.CameraUnInit(self.hCamera)
        mvsdk.CameraAlignFree(self.pFrameBuffer)



### Experimental parameter settings ###--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Set Temparatures ##
set_working_temps = [10, 20, 30, 40, 50] 
set_initial_temp = 20 

## Set anolyte concnetrations of interest (The concentrations of hydroxyl groups of alchols, mmol/L) ##
concentrated_anolytes = 80 
dilution_anolytes = 0
concenration_anolytes = [40, 40, 40, 40, 40]
dilution_factor_anolytes = []
for i in range(len(concenration_anolytes)):
    dilution_factor_anolytes.append(concenration_anolytes[i]/concentrated_anolytes)

## Set cathode concentrations of interest (NaOH, mol/L) ##
concentrated_catholytes = 1
dilution_catholytes = 0
concentration_catholytes = [0.5, 0.5, 0.5, 0.5, 0.5]
dilution_factor_catholytes = []
for i in range(len(concentration_catholytes)):
    dilution_factor_catholytes.append(concentration_catholytes[i]/concentrated_catholytes)

## Set working flow rates of two elecrolytes ##
flow_rate_anolytes = [300, 300, 300, 300]   # =  A1 + A2, Working electrode
flow_rate_catholytes = [300, 300, 300, 300]     # =  B1 + B2, Counter electrode
flow_rate_A1 = []  #concentrated_anolyte
flow_rate_A2 = []  #diluton_anolyte
flow_rate_B1 = []  #concentrated_anolyte
flow_rate_B2 = []  #diluton_catholyte
 
for i in range(len(dilution_factor_anolytes)):
    flow_rate_A1.append(flow_rate_anolytes[i] * dilution_factor_anolytes[i])
    flow_rate_A2.append(flow_rate_anolytes[i] * (1-dilution_factor_anolytes[i]))
    flow_rate_B1.append(flow_rate_catholytes[i] * dilution_factor_catholytes[i])
    flow_rate_B2.append(flow_rate_catholytes[i] * (1-dilution_factor_catholytes[i]))
 
## Set flow rates and times
time_for_bubble_removal = 60 #unit: seconds
time_for_washing = 60 #unit: seconds
time_for_flushing_electrode = 30 #unit: seconds
time_for_flow_rate_stable = 30 #unit: seconds

flow_rate_for_waiting_temp = 50 #unit: uL/min
flow_rate_for_flushing_electrode = 600 #unit: uL/min
flow_rate_for_cleaning_electrode_with_CVs = 150 #unit: uL/min
flow_rate_for_bubble_removal = 400 #unit: uL/min
flow_rate_for_washing_system = 200 #unit: uL/min    
    
## Set electrochemical workstation parameters ##
# Select the potentiostat model to use:
model = 'chi760e'
# Pauth to the chi software, including extension .exe
path = 'C:\Software\Workstation\chi660e\chi660e.exe'

# Folder where to save the data
dir_path = os.path.dirname(os.path.abspath(__file__))
folder='test'
folder_path = os.path.join(dir_path, folder)
os.makedirs(folder_path, exist_ok=True)

# CV measurements
Eini = 0.25     # V, initial potential
Ev1 = 0.55       # V, first vertex potential
Ev2 = 0.4      # V, second vertex potential
Efin = 0.3     # V, final potential
sr = 0.002         # V/s, scan rate
dE = 0.001      # V, potential increment
nSweeps = 1     # number of sweeps 
sens = 1e-4     # A/V, current sensitivity
E2 = 0.5        # V, potential of the second working electrode
sens2 = 1e-4    # A/V, current sensitivity of the second working electrode 

measurement_time =  (Ev1 - Eini) / sr * nSweeps # Measurement time for each CV or LSV test (s)
      
# CVs for electrode cleaning
Eini_cleaning = 0.2     # V, initial potential
Ev1_cleaning = 0.6       # V, first vertex potential
Ev2_cleaning = 0.2      # V, second vertex potential
Efin_cleaning = 0.2     # V, final potential
sr_cleaning = 0.1         # V/s, scan rate
dE_cleaning = 0.001      # V, potential increment
nSweeps_cleaning = 200     # number of sweeps 
sens_cleaning = 1e-3     # A/V, current sensitivity
E2_cleaning = 0.5        # V, potential of the second working electrode
sens2_cleaning = 1e-4    # A/V, current sensitivity of the second working electrode

## Set Vavle positions ##
valve1_positions = [0,1,2,3,4,5,6,7] # position 0 is for the washing solvent (0.5M NaOH); positions 1,2,3,4,5,6 are for electrolytes with contianing different alchols; position 7 is for air
valve2_positions = [0,1]  # position 0 is for the catholyte (0.5M NaOH); position 1 is for air



### Connect to devices and dispaly current settings ###-------------------------------------------------------------------------------------------------------------------

## Connect to water bath ##
try: 
    bath = serial.Serial(
        'COM5',
        baudrate=19200,
        bytesize=8,
        timeout=1
    )

    print('***********************************')
    print('Serial connection established on')
    print(bath.name)  # print port info
    print('***********************************')
    time.sleep(2)

    bath.write("RT\r".encode('utf-8'))
    response = bath.readline()
    print("Current bath temperature: %s" % response.decode('utf-8'))

    bath.write("RS\r".encode('utf-8'))
    response = bath.readline()
    print("Current bath setpoint: %s" % response.decode('utf-8'))
    
except serial.SerialException as e:
    print("++++++++++++++++++++++++++")
    print("Serial connection failed", e)
    print("++++++++++++++++++++++++++")

## Connect to flow sensors and pumps ##
print('Current flow rate A1: {}'.format(fgt_get_sensorValue(0)))
print('Current flow rate A2: {}'.format(fgt_get_sensorValue(1)))
print('Current flow rate B1: {}'.format(fgt_get_sensorValue(2)))
print('Current flow rate B2: {}'.format(fgt_get_sensorValue(3)))

## Connect to Valve ##
# Get valve indices
valve_indices = range(fgt_get_valveChannelCount())
# Two valve used 
valve1_index = 0
valve2_index = 1
print("Current valve 1 position {}".format(fgt_get_valvePosition(valve1_index)))
print("Current valve 2 position {}".format(fgt_get_valvePosition(valve2_index)))

if not valve_indices:
    raise Exception("No valve channels found")

## Connect to Electrochemical workstation ##
# Initialization:
hp.potentiostat.Setup(model=model, path=path, folder=folder)



### Run experiments ###--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Run measurements for alchols i at different temparetures
for valve_position in valve1_positions:
    
    # Wash the system after finishing each alchol test
    print()
    print('---- Put valve1 position to 0 to wash the system ----')
    
    fgt_set_valvePosition(valve1_index, 0) # position 0 is the washing solvent
    fgt_set_valvePosition(valve2_index, 0) # position 0 is the catholyte, also the washing solvent
    fgt_set_sensorRegulation(0, 0, flow_rate_for_washing_system) # set flow rate of A1
    fgt_set_sensorRegulationResponse (0, 60)
    fgt_set_sensorRegulation(1, 1, flow_rate_for_washing_system) # set flow rate of A2
    fgt_set_sensorRegulationResponse (1, 60)
    fgt_set_sensorRegulation(2, 2, flow_rate_for_washing_system) # set flow rate of B1
    fgt_set_sensorRegulationResponse (2, 60)
    fgt_set_sensorRegulation(3, 3, flow_rate_for_washing_system) # set flow rate of B2
    fgt_set_sensorRegulationResponse (3, 60)

    print('Waiting {:.0f} seconds...'.format(time_for_washing))
    time.sleep(time_for_washing)
    
    # Wait the temp to reach the initial value 
    print()
    print('---- Set the tempareture to intinial value {:0.2f} C ----'.format(set_initial_temp))
    
    fgt_set_sensorRegulation(0, 0, flow_rate_for_waiting_temp) # set flow rate of A1
    fgt_set_sensorRegulationResponse (0, 60)
    fgt_set_sensorRegulation(1, 1, flow_rate_for_waiting_temp) # set flow rate of A2
    fgt_set_sensorRegulationResponse (1, 60)
    fgt_set_sensorRegulation(2, 2, flow_rate_for_waiting_temp) # set flow rate of B1
    fgt_set_sensorRegulationResponse (2, 60)
    fgt_set_sensorRegulation(3, 3, flow_rate_for_waiting_temp) # set flow rate of B2
    fgt_set_sensorRegulationResponse (3, 60)
    
    bath.write("SO 1\r".encode('utf-8'))  # set status of bath to on/run
    response = bath.readline()
    
    flag = False
    
    while flag != True:
        command = "SS %2.2f\r" % float(set_initial_temp)
        bath.write(command.encode('utf-8'))
        response = bath.readline()

        bath.write("RS\r".encode('utf-8'))
        response = bath.readline()

        bath.write("RT\r".encode('utf-8'))
        response = bath.readline()
        current_temp = float(response.decode('utf-8').strip().replace('C', ''))
        
        # Get flow rate value
        measured_flow_rate_anolyte = fgt_get_sensorValue(0)+fgt_get_sensorValue(1)
        measured_flow_rate_catholyte = fgt_get_sensorValue(2)+fgt_get_sensorValue(3)
        
        print("S_T: %2.2f C     C_T: %s C    S_QA : %2.0f uL/min   S_QB : %2.0f uL/min    C_QA : %2.0f uL/min    C_QB : %2.0f uL/min" % (set_initial_temp, current_temp, flow_rate_for_waiting_temp*2, flow_rate_for_waiting_temp*2, measured_flow_rate_anolyte, measured_flow_rate_catholyte))

        if format(current_temp, '.1f') == format(set_initial_temp, '.1f'):
            print("Reach the initial setpoint: %s C" % current_temp)
            
            n = 10 
            while n > 0:
                time.sleep(1)
                n -= 1
                
            flag = True    
    
    # Run temprature ramping for alchol i and conduct EC tests
    print()
    print('---- Start testing alchol {:.0f} ----'.format(valve_position))
    
    for j in range(len(set_working_temps)):
        
        print()
        print('0. Put valve position to 0 and set flow rates to wash the system')
        print('Waiting {:.0f} seconds...'.format(time_for_washing))
        fgt_set_valvePosition(valve1_index, 0) # position 0 is the washing solvent
        fgt_set_valvePosition(valve2_index, 0) # position 0 is the catholyte, also the washing solvent
        fgt_set_sensorRegulation(0, 0, flow_rate_for_washing_system) # set flow rate of A1
        fgt_set_sensorRegulationResponse (0, 60)
        fgt_set_sensorRegulation(1, 1, flow_rate_for_washing_system) # set flow rate of A2
        fgt_set_sensorRegulationResponse (1, 60)
        fgt_set_sensorRegulation(2, 2, flow_rate_for_washing_system) # set flow rate of B1
        fgt_set_sensorRegulationResponse (2, 60)
        fgt_set_sensorRegulation(3, 3, flow_rate_for_washing_system) # set flow rate of B2
        fgt_set_sensorRegulationResponse (3, 60)
        time.sleep (time_for_washing)
        
        print('1. Put valve position to {:.0f} and set flow rates to remove the washing solvent'.format(valve_position))
        print('Waiting {:.0f} seconds...'.format(time_for_washing))
        fgt_set_valvePosition(valve1_index, valve_position) # position valve_position is the alchol i
        fgt_set_valvePosition(valve2_index, 0) # position 0 is the catholyte
        fgt_set_sensorRegulation(0, 0, flow_rate_for_washing_system) # set flow rate of A1
        fgt_set_sensorRegulationResponse (0, 60)
        fgt_set_sensorRegulation(1, 1, flow_rate_for_washing_system) # set flow rate of A2
        fgt_set_sensorRegulationResponse (1, 60)
        fgt_set_sensorRegulation(2, 2, flow_rate_for_washing_system) # set flow rate of B1
        fgt_set_sensorRegulationResponse (2, 60)
        fgt_set_sensorRegulation(3, 3, flow_rate_for_washing_system) # set flow rate of B2
        fgt_set_sensorRegulationResponse (3, 60)
        time.sleep (time_for_washing)
        
        print('2. Set flow rates for waiting tempareture to reach the set value')
        fgt_set_sensorRegulation(0, 0, flow_rate_for_waiting_temp) # set flow rate of A1
        fgt_set_sensorRegulationResponse (0, 60)
        fgt_set_sensorRegulation(1, 1, flow_rate_for_waiting_temp) # set flow rate of A2
        fgt_set_sensorRegulationResponse (1, 60)
        fgt_set_sensorRegulation(2, 2, flow_rate_for_waiting_temp) # set flow rate of B1
        fgt_set_sensorRegulationResponse (2, 60)
        fgt_set_sensorRegulation(3, 3, flow_rate_for_waiting_temp) # set flow rate of B2
        fgt_set_sensorRegulationResponse (3, 60)
        
        print('3. Set the tempareture to {:.2f}, and wait'.format(set_working_temps[j]))   
        bath.write("SO 1\r".encode('utf-8'))  # set status of bath to on/run
        response = bath.readline()
        
        flag = False
        
        while not flag:
            command = "SS %2.2f\r" % float(set_working_temps[j])
            bath.write(command.encode('utf-8'))
            response = bath.readline()

            bath.write("RS\r".encode('utf-8'))
            response = bath.readline()

            bath.write("RT\r".encode('utf-8'))
            response = bath.readline()
            current_temp = float(response.decode('utf-8').strip().replace('C', ''))
            
            # Get flow rate value
            measured_flow_rate_anolyte = fgt_get_sensorValue(0)+fgt_get_sensorValue(1)
            measured_flow_rate_catholyte = fgt_get_sensorValue(2)+fgt_get_sensorValue(3)
            
            print("S_T: %2.2f C     C_T: %s C     S_QA : %2.0f uL/min   S_QB : %2.0f uL/min    C_QA : %2.0f uL/min    C_QB : %2.0f uL/min" % (set_working_temps[j], current_temp, flow_rate_for_waiting_temp*2, flow_rate_for_waiting_temp*2, measured_flow_rate_anolyte, measured_flow_rate_catholyte))

            if format(current_temp, '.1f') == format(set_working_temps[j], '.1f'):
                
                print("4. Reach the setpoint: %s C, change to working flow rates" % current_temp)
                
                fgt_set_sensorRegulation(0, 0, flow_rate_A1[j]) # set flow rate of A1
                fgt_set_sensorRegulationResponse (0, 60)
                fgt_set_sensorRegulation(1, 1, flow_rate_A2[j]) # set flow rate of A2
                fgt_set_sensorRegulationResponse (1, 60)
                fgt_set_sensorRegulation(2, 2, flow_rate_B1[j]) # set flow rate of B1
                fgt_set_sensorRegulationResponse (2, 60)
                fgt_set_sensorRegulation(3, 3, flow_rate_B2[j]) # set flow rate of B2
                fgt_set_sensorRegulationResponse (3, 60)
                
                time.sleep(time_for_flow_rate_stable)
                
                print("5. Run CV or LSV measurments")
                # set CV method
                msr = sr*1000
                mEini = Eini*1000
                mEv1 = Ev1*1000
                fileName = '{:.0f}_'.format(valve_position)+'{:.0f}mV'.format(mEini)+'_{:.0f}mV'.format(mEv1)+'_{:.0f}mVs'.format(msr)+'_{:.0f}oC'.format(set_working_temps[j]) # base file name for data file
                header = 'CV'   # header for data filef"file_{x}.txt"

                # Initialize experiment:
                cv = hp.potentiostat.CV(Eini, Ev1, Ev2, Efin, sr, dE, nSweeps, sens, fileName, header)

                # Create a CameraRecorder object
                video_save_path = os.path.join(folder_path, fileName + ".mp4")
                camera_recorder = CameraRecorder(measurement_time, video_save_path)

                # Start CV thread
                cv_thread = threading.Thread(target=cv.run)
                cv_thread.start()

                # Add a slight delay before starting the camera thread
                time.sleep(1)  # Adjust the delay as needed

                camera_thread = threading.Thread(target=camera_recorder.start_recording)
                camera_thread.start()

                # Wait after running 
                time.sleep(measurement_time)

                print("6. CV test and video recording finished, clean the electrode") 
                # Flush electrode
                fgt_set_valvePosition(valve1_index, 0) # position 0 is the washing solvent
                fgt_set_valvePosition(valve2_index, 0) # position 0 is the catholyte, also the washing solvent
                fgt_set_sensorRegulation(0, 0, flow_rate_for_flushing_electrode) # set flow rate of A1
                fgt_set_sensorRegulationResponse (0, 60)
                fgt_set_sensorRegulation(1, 1, flow_rate_for_flushing_electrode) # set flow rate of A2
                fgt_set_sensorRegulationResponse (1, 60)
                fgt_set_sensorRegulation(2, 2, flow_rate_for_flushing_electrode) # set flow rate of B1
                fgt_set_sensorRegulationResponse (2, 60)
                fgt_set_sensorRegulation(3, 3, flow_rate_for_flushing_electrode) # set flow rate of B2
                fgt_set_sensorRegulationResponse (3, 60)
                
                time.sleep(time_for_flow_rate_stable + time_for_flushing_electrode)
                
                # Run CVs for electrode cleaning                
                fgt_set_sensorRegulation(0, 0, flow_rate_for_cleaning_electrode_with_CVs) # set flow rate of A1
                fgt_set_sensorRegulationResponse (0, 60)
                fgt_set_sensorRegulation(1, 1, flow_rate_for_cleaning_electrode_with_CVs) # set flow rate of A2
                fgt_set_sensorRegulationResponse (1, 60)
                fgt_set_sensorRegulation(2, 2, flow_rate_for_cleaning_electrode_with_CVs) # set flow rate of B1
                fgt_set_sensorRegulationResponse (2, 60)
                fgt_set_sensorRegulation(3, 3, flow_rate_for_cleaning_electrode_with_CVs) # set flow rate of B2
                fgt_set_sensorRegulationResponse (3, 60)
                
                time.sleep(time_for_flow_rate_stable)
                
                fileName_cleaning = '{:.0f}_'.format(valve_position)+'_{:.0f}oC'.format(set_working_temps[j]) # base file name for data file
                header_cleaning = 'CV_cleaning'   # header for data filef"file_{x}.txt"

                cv = hp.potentiostat.CV(Eini_cleaning, Ev1_cleaning, Ev2_cleaning, Efin_cleaning, sr_cleaning, dE_cleaning, nSweeps_cleaning, sens_cleaning, fileName_cleaning, header_cleaning)

                cv.run()
                
                print ("7. Introduce air bubbles to remove the trapped bubbles")
                fgt_set_sensorRegulation(0, 0, flow_rate_for_bubble_removal) # set flow rate of A1
                fgt_set_sensorRegulationResponse (0, 60)
                fgt_set_sensorRegulation(1, 1, flow_rate_for_bubble_removal) # set flow rate of A2
                fgt_set_sensorRegulationResponse (1, 60)
                fgt_set_sensorRegulation(2, 2, flow_rate_for_bubble_removal) # set flow rate of B1
                fgt_set_sensorRegulationResponse (2, 60)
                fgt_set_sensorRegulation(3, 3, flow_rate_for_bubble_removal) # set flow rate of B2
                fgt_set_sensorRegulationResponse (3, 60)
                time.sleep(time_for_flow_rate_stable)
                
                # introduce air bubbles
                fgt_set_valvePosition(valve1_index, 7) # position 7 is the air
                fgt_set_valvePosition(valve2_index, 1) # position 1 is the air
                time.sleep(2)
                
                fgt_set_valvePosition(valve1_index, 0) # position 0 is the washing solvent
                fgt_set_valvePosition(valve2_index, 0) # position 0 is the catholyte, also the washing solvent

                # Wait  
                time.sleep(time_for_bubble_removal) 
                
                flag = True
        
### Wash the flow system ###--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Wash the system after finishing all tests
print()
print('---- All tests finished, put valve position to 0 to wash the system and cool the tempature ----')

fgt_set_valvePosition(valve1_index, 0) # position 0 is the washing solvent
fgt_set_valvePosition(valve2_index, 0) # position 0 is the catholyte, also the washing solvent

fgt_set_sensorRegulation(0, 0, flow_rate_for_washing_system) # set flow rate of A1
fgt_set_sensorRegulationResponse (0, 60)
fgt_set_sensorRegulation(1, 1, flow_rate_for_washing_system) # set flow rate of A2
fgt_set_sensorRegulationResponse (1, 60)
fgt_set_sensorRegulation(2, 2, flow_rate_for_washing_system) # set flow rate of B1
fgt_set_sensorRegulationResponse (2, 60)
fgt_set_sensorRegulation(3, 3, flow_rate_for_washing_system) # set flow rate of B2
fgt_set_sensorRegulationResponse (3, 60)
time.sleep (time_for_washing)

fgt_set_sensorRegulation(0, 0, flow_rate_for_waiting_temp) # set flow rate of A1
fgt_set_sensorRegulationResponse (0, 60)
fgt_set_sensorRegulation(1, 1, flow_rate_for_waiting_temp) # set flow rate of A2
fgt_set_sensorRegulationResponse (1, 60)
fgt_set_sensorRegulation(2, 2, flow_rate_for_waiting_temp) # set flow rate of B1
fgt_set_sensorRegulationResponse (2, 60)
fgt_set_sensorRegulation(3, 3, flow_rate_for_waiting_temp) # set flow rate of B2
fgt_set_sensorRegulationResponse (3, 60)

bath.write("SO 1\r".encode('utf-8'))  # set status of bath to on/run
response = bath.readline()

flag = False

while flag != True:
    command = "SS %2.2f\r" % float(set_initial_temp)
    bath.write(command.encode('utf-8'))
    response = bath.readline()

    bath.write("RS\r".encode('utf-8'))
    response = bath.readline()

    bath.write("RT\r".encode('utf-8'))
    response = bath.readline()
    current_temp = float(response.decode('utf-8').strip().replace('C', ''))
    
    # Get flow rate value
    measured_flow_rate_anolyte = fgt_get_sensorValue(0)+fgt_get_sensorValue(1)
    measured_flow_rate_catholyte = fgt_get_sensorValue(2)+fgt_get_sensorValue(3)
    
    print("S_T: %2.2f C     C_T: %s C    S_QA : %2.0f uL/min   S_QB : %2.0f uL/min    C_QA : %2.0f uL/min    C_QB : %2.0f uL/min" % (set_initial_temp, current_temp, flow_rate_for_waiting_temp*2, flow_rate_for_waiting_temp*2, measured_flow_rate_anolyte, measured_flow_rate_catholyte))

    if format(current_temp, '.1f') == format(set_initial_temp, '.1f'):
        print("Reach the initial setpoint: %s C" % current_temp)
        
        n = 10 
        while n > 0:
            time.sleep(1)
            n -= 1
            
        flag = True    

## Close the session
# Set pressure to 0 before closing. This also stops the regulation
fgt_set_pressure(0, 0)
fgt_close()


