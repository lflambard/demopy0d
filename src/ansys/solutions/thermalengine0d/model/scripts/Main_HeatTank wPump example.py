# MAIN
import numpy as np
import matplotlib.pyplot as plt
import math
import time
from configparser import ConfigParser
from ansys.solutions.thermalengine0d.model.Library_Fluid_class import VolumeFluid_C, FlowSourceFluid, PumpFluid
from ansys.solutions.thermalengine0d.model.Library_Control_class import PI_control


time1 = time.time()
"-----------------------------------------------------------"
"SIMULATION PARAMETER"
"-----------------------------------------------------------"
start_simu = 0
end_simu = 7500
step_simu = 0.01
sample_time = 0.1
LastVal = (end_simu - start_simu) / step_simu

"-----------------------------------------------------------"
"SIMULATION CONFIG IMPORT"
"-----------------------------------------------------------"
config = ConfigParser()


"-----------------------------------------------------------"
"INIT"
"-----------------------------------------------------------"
P0 = 150000
T0 = 293
Cp_water = 4180
Rho_water = 1000
h_air = 8; "convection coefficient for air W/m²/K"
BulkModulus_water = 2e9
Height_Tank = 1.5
Diameter_Tank = 0.3
Surface_Tank = math.pi * Diameter_Tank ** 2 / 2 + math.pi * Diameter_Tank * Height_Tank
Volume_Tank = math.pi * Diameter_Tank ** 2 / 4 * Height_Tank
T_control = 500
DeltaTPump_max = 50
Flow_init = FlowSourceFluid(0, T0 * Cp_water)

"Creation of vectors for saving / plots"
result_simu = np.zeros((int(LastVal+1 * step_simu / sample_time), 9))
time_simu = np.arange(1, LastVal+2)

"-----------------------------------------------------------"
"MODEL CREATION"
"-----------------------------------------------------------"
HeatTank = VolumeFluid_C(Flow_init.F, Flow_init.F, 0, P0, T0)
Pump = PumpFluid(HeatTank.E1, HeatTank.E2, 0, 0)
PI_Heat = PI_control(T0, T0)

"-----------------------------------------------------------"
"MODEL PARAM"
"-----------------------------------------------------------"
HeatTank.Param(Volume_Tank, Cp_water, Rho_water, BulkModulus_water)
Pump.Param([0, 10], [0, 0.001], Rho_water, Cp_water)
PI_Heat.Param(0.1, 0.1, 0, 10)

"-----------------------------------------------------------"
"SIMULATION"
"-----------------------------------------------------------"
time_simu[0] = start_simu
incr_save_old = 0
print ("time="+repr(time_simu[0]))
result_simu[0, 0] = time_simu[0]
result_simu[0, 1] = T_control - 273
result_simu[0, 2] = T0 - 273
result_simu[0, 3] = P0 / 1e5
result_simu[0, 4] = 0
result_simu[0, 5] = 0
result_simu[0, 6] = T0 - 273
result_simu[0, 7] = 0

method = 'Euler'

for i in range(1, int(LastVal+1)):
    time_simu[i] = i * step_simu + start_simu

    "Heat Control"
    PI_Heat.x_Ord = T_control
    PI_Heat.x_Act = HeatTank.E1.T
    PI_Heat.Solve(step_simu, method)

    "Pump"
    Pump.E1 = HeatTank.E2
    Pump.E2 = HeatTank.E1
    Pump.Ee = PI_Heat.y
    Pump.Phi = Pump.F2.Qm * Rho_water * DeltaTPump_max
    Pump.Solve()

    "Heat Tank - non adiabatic Tank (Thermal losses)"
    HeatTank.F1 = Pump.F2
    HeatTank.F2 = Pump.F1
    Phi_convection = h_air * Surface_Tank * (T0 - HeatTank.E2.T)
    HeatTank.Phi = Phi_convection
    HeatTank.Solve(step_simu, method)


    "-----------------------------------------------------------"
    "Save results according to the defined sample time"
    "-----------------------------------------------------------"
    incr_save = math.floor(i * step_simu / sample_time)
    if incr_save > incr_save_old:
        print ("time="+repr(time_simu[i]))
        result_simu[incr_save, 0] = time_simu[i]
        result_simu[incr_save, 1] = T_control - 273
        result_simu[incr_save, 2] = HeatTank.E2.T - 273
        result_simu[incr_save, 3] = HeatTank.E1.P / 1e5
        result_simu[incr_save, 4] = PI_Heat.y
        result_simu[incr_save, 5] = Pump.F2.Qm
        result_simu[incr_save, 6] = Pump.T2 - 273
        result_simu[incr_save, 7] = Pump.Phi
        result_simu[incr_save, 8] = - HeatTank.Phi

    incr_save_old = incr_save

time2 = time.time()
print("Time for Simulation", repr(round((time2 - time1)*10)/10))
"-----------------------------------------------------------"
"PLOTS"
"-----------------------------------------------------------"
plt.figure(1)
plt.subplot(231)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 2],'b',result_simu[0:incr_save, 0],result_simu[0:incr_save, 1],'r')
plt.ylabel('Heat tank temperature [°C]')
plt.subplot(232)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 4],'b')
plt.ylabel('Pump current [A]')
plt.subplot(233)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 3])
plt.xlabel('time [s]')
plt.ylabel('Heat Tank Pressure [Bar]')
plt.subplot(234)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 5])
plt.xlabel('time [s]')
plt.ylabel('Pump flow [kg/s]')
plt.subplot(235)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 2],'b',result_simu[0:incr_save, 0], result_simu[0:incr_save, 6],'g')
plt.xlabel('time [s]')
plt.ylabel('Pump Temperature [K]')
plt.subplot(236)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 7],'b',result_simu[0:incr_save, 0], result_simu[0:incr_save, 8],'g')
plt.xlabel('time [s]')
plt.ylabel('Phi [W]')
plt.show()
