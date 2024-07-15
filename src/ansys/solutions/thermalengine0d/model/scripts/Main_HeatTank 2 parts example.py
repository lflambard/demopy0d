# MAIN
import numpy as np
import matplotlib.pyplot as plt
import math
import time
from configparser import ConfigParser
from ansys.solutions.thermalengine0d.model.Library_Fluid_class import VolumeFluid_C, FlowSourceFluid
from ansys.solutions.thermalengine0d.model.Library_Control_class import PI_control


time1 = time.time()
"-----------------------------------------------------------"
"SIMULATION PARAMETER"
"-----------------------------------------------------------"
start_simu = 0
end_simu = 50
step_simu = 1
sample_time = 1
LastVal = (end_simu - start_simu) / step_simu

"-----------------------------------------------------------"
"SIMULATION CONFIG IMPORT"
"-----------------------------------------------------------"
config = ConfigParser()


"-----------------------------------------------------------"
"INIT"
"-----------------------------------------------------------"
P0 = 150000
T0 = 300
Tout = 295
Cp_water = 4182
Rho_water = 0.5
h_air = 10; "convection coefficient for air W/m²/K"
h_tank = 30
BulkModulus_water = 2e9
Height_Tank = 0.14
Diameter_Tank = 0.05 * 2
Surface_Tank = math.pi * Diameter_Tank ** 2 / 4
Volume_Tank = math.pi * Diameter_Tank ** 2 / 4 * Height_Tank
T_control = 350
Flow_init = FlowSourceFluid(0, T0 * Cp_water)

"Creation of vectors for saving / plots"
result_simu = np.zeros((int(LastVal+1 * step_simu / sample_time), 5))
time_simu = np.arange(1, LastVal+2)

"-----------------------------------------------------------"
"MODEL CREATION"
"-----------------------------------------------------------"
HeatTank1 = VolumeFluid_C(Flow_init.F, Flow_init.F, 0, P0, T0)
HeatTank2 = VolumeFluid_C(Flow_init.F, Flow_init.F, 0, P0, T0)
PI_Heat = PI_control(T0, T0)

"-----------------------------------------------------------"
"MODEL PARAM"
"-----------------------------------------------------------"
HeatTank1.Param(Volume_Tank / 2, Cp_water, Rho_water, BulkModulus_water)
HeatTank2.Param(Volume_Tank / 2, Cp_water, Rho_water, BulkModulus_water)
PI_Heat.Param(1, 0.5, 0, 10)

"-----------------------------------------------------------"
"SIMULATION"
"-----------------------------------------------------------"
time_simu[0] = start_simu
incr_save_old = 0
print ("time="+repr(time_simu[0]))
result_simu[0, 0] = time_simu[0]
result_simu[0, 1] = T_control
result_simu[0, 2] = T0
result_simu[0, 3] = P0
result_simu[0, 4] = 0

method = 'Euler'

for i in range(1, int(LastVal+1)):
    time_simu[i] = i * step_simu + start_simu

    "Heat Control"
    PI_Heat.x_Ord = T_control
    PI_Heat.x_Act = HeatTank2.E1.T
    PI_Heat.Solve(step_simu, method)

    "Heat Tank1"
    Phi_transfer = h_tank * Surface_Tank * (HeatTank2.E2.T - HeatTank1.E2.T)
    HeatTank1.Phi = PI_Heat.y + Phi_transfer
    HeatTank1.Solve(step_simu, method)

    "Heat Tank2"
    Phi_convection = h_air * Surface_Tank * (Tout - HeatTank2.E2.T)
    HeatTank2.Phi = - Phi_transfer + Phi_convection
    HeatTank2.Solve(step_simu, method)


    "-----------------------------------------------------------"
    "Save results according to the defined sample time"
    "-----------------------------------------------------------"
    incr_save = math.floor(i * step_simu / sample_time)
    if incr_save > incr_save_old:
        print ("time="+repr(time_simu[i]))
        result_simu[incr_save, 0] = time_simu[i]
        result_simu[incr_save, 1] = T_control
        result_simu[incr_save, 2] = HeatTank2.T
        result_simu[incr_save, 3] = HeatTank2.E1.P
        result_simu[incr_save, 4] = PI_Heat.y


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
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 4],'b')
plt.ylabel('Heating Flow [W]')
plt.subplot(223)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 3])
plt.xlabel('time [s]')
plt.ylabel('Heat Tank Pressure [Pa]')
plt.show()
