# MAIN
import numpy as np
import matplotlib.pyplot as plt
import math
import time
import tkinter as tk
from tkinter.filedialog import askopenfilename
from configparser import ConfigParser
from ansys.solutions.thermalengine0d.model.scripts.Import_Model import ImportModel
from ansys.solutions.thermalengine0d.model.Library_Fluid_class import VolumeFluid_C, VolumeFluid_C_2HEX, FlowSourceFluid, PumpFluid
from ansys.solutions.thermalengine0d.model.Library_Control_class import PI_control, Input_control
from ansys.solutions.thermalengine0d.model.Library_Thermal_class import EffortSourceTH, FlowSourceTH, HET_R

time1 = time.time()
"-----------------------------------------------------------"
"SIMULATION PARAMETER"
"-----------------------------------------------------------"
start_simu = 0
end_simu = 7500
step_simu = 0.1
sample_time = 1
LastVal = (end_simu - start_simu) / step_simu
method = 'Euler'
time_simu = np.arange(1, LastVal+2)
time_simu[0] = start_simu

"-----------------------------------------------------------"
"SIMULATION CONFIG IMPORT"
"-----------------------------------------------------------"
config = ConfigParser()


"-----------------------------------------------------------"
"MODEL CREATION"
"-----------------------------------------------------------"
root = tk.Tk()
root.withdraw()
name_file = askopenfilename(filetypes=(("Excel file", "*.xls"), ("All Files", "*.*")),
                            title="Choose a file for Model Import."
                            )
Model = ImportModel(name_file)
Model.Model_creation()
exec(Model.model_blocks)


"-----------------------------------------------------------"
"MODEL PARAM"
"-----------------------------------------------------------"
exec(Model.model_param)

"-----------------------------------------------------------"
"SIMULATION"
"-----------------------------------------------------------"
exec(Model.model_result_init)
incr_save_old = 0
print ("time="+repr(time_simu[0]))


for i in range(1, int(LastVal+1)):
    time_simu[i] = i * step_simu + start_simu
    exec(Model.model_solve)


    "-----------------------------------------------------------"
    "Save results according to the defined sample time"
    "-----------------------------------------------------------"
    incr_save = math.floor(i * step_simu / sample_time)
    if incr_save > incr_save_old:
        print ("time="+repr(time_simu[i]))
        exec(Model.model_result)
    incr_save_old = incr_save

time2 = time.time()
print("Time for Simulation", repr(round((time2 - time1)*10)/10))

"-----------------------------------------------------------"
"PLOTS"
"-----------------------------------------------------------"
plt.figure(1)
plt.subplot(221)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 2],'r',result_simu[0:incr_save, 0],result_simu[0:incr_save, 1],'g')
plt.ylabel('Heat tank temperature [K]')
plt.subplot(222)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 3],'b')
plt.ylabel('Heating Flow [W]')
plt.subplot(223)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 4])
plt.xlabel('time [s]')
plt.ylabel('Heat Tank Pressure [Pa]')
if result_simu.shape[1]>5:
    plt.subplot(224)
    plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 5], 'b',result_simu[0:incr_save, 0], result_simu[0:incr_save, 6], 'g', result_simu[0:incr_save, 0], result_simu[0:incr_save, 2], 'r')
    plt.ylabel('Heat tank Parts temperature [K]')
plt.show()
