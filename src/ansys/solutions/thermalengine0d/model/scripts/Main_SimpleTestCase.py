# MAIN
import numpy as np
import matplotlib.pyplot as plt
import math
import time
from configparser import ConfigParser
from ansys.solutions.thermalengine0d.model.Library_ThermoFluid_class import Compressor_Tf, PressureLosses_R, Volume_C, EffortSource, FlowSource
from ansys.solutions.thermalengine0d.model.scripts.Fluid_properties_class import FluidFuel
from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import EffortM, FlowM
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolv

time1 = time.time()
"-----------------------------------------------------------"
"SIMULATION PARAMETER"
"-----------------------------------------------------------"
start_simu = 0
end_simu = 10
step_simu = 0.001
sample_time = 0.01
LastVal = (end_simu - start_simu) / step_simu

"-----------------------------------------------------------"
"SIMULATION CONFIG IMPORT"
"-----------------------------------------------------------"
config = ConfigParser()
config.read('ModelSimple_init.ini')

"-----------------------------------------------------------"
"INIT"
"-----------------------------------------------------------"
Pair = 1e5
Tair = 298
P0 = 90000
T0 = 293
Ks = 14.4
LHV = 42800000
Hv = 230000
nC = 10.8
nH = 18.7
Nturbo = 120000

Fuel = FluidFuel(Ks, LHV, Hv, nC, nH)
Ambient_Air = EffortSource(Pair, Tair)
Flow_init = FlowSource(0, T0)

"Creation of vectors for saving / plots"
result_simu = np.zeros((int(LastVal+1 * step_simu / sample_time), 9))
time_simu = np.arange(1, LastVal+2)

"-----------------------------------------------------------"
"MODEL CREATION"
"-----------------------------------------------------------"
AirFilter = PressureLosses_R(Ambient_Air.E, Ambient_Air.E)
VolumeAirFilter = Volume_C(Flow_init.F, Flow_init.F)
Compressor = Compressor_Tf(Ambient_Air.E, Ambient_Air.E, FlowM(Nturbo / 30 * math.pi))
VolumeCompr = Volume_C(Flow_init.F, Flow_init.F)

"-----------------------------------------------------------"
"MODEL PARAM"
"-----------------------------------------------------------"
AirFilter.Param(eval(config['AirFilter_param']['k_pl_af']))
VolumeAirFilter.Param(eval(config['AirFilter_param']['vol_af']))
Compressor.Param(eval(config['Compr_param']['prefc']), eval(config['Compr_param']['trefc']),
                 eval(config['Compr_param']['x_nc']), eval(config['Compr_param']['surge_pr']),
                 eval(config['Compr_param']['y_margin']), eval(config['Compr_param']['z_flow_cor']),
                 eval(config['Compr_param']['z_eta_comp']))
VolumeCompr.Param(eval(config['Compr_param']['vol_compr']))
"-----------------------------------------------------------"
"SIMULATION"
"-----------------------------------------------------------"
time_simu[0]=start_simu
incr_save_old = 0
method = 'Euler'

for i in range(1, int(LastVal+1)):
    time_simu[i] = i * step_simu + start_simu
    "Pedal position=f(time_simu)"
    N = interpolv([0, 5, 5.01, 10.5, 10.51, 15], [120000, 120000, 150000, 150000, 130000, 130000], time_simu[i])

    "AirFilter"
    AirFilter.E1 = Ambient_Air.E
    AirFilter.E2 = VolumeAirFilter.E1
    AirFilter.Solve()
    VolumeAirFilter.F1 = AirFilter.F2
    VolumeAirFilter.F2 = Compressor.F1
    VolumeAirFilter.Solve(step_simu, method)

    "Compressor"
    Compressor.E1 = VolumeAirFilter.E2
    Compressor.E2 = VolumeCompr.E1
    Compressor.Fm = FlowM(N / 30 * math.pi)
    Compressor.Solve()
    VolumeCompr.F1 = Compressor.F2
    VolumeCompr.F2 = FlowSource(-0.1, Compressor.E2.T)
    VolumeCompr.Solve(step_simu, method)

    "-----------------------------------------------------------"
    "Save results according to the defined sample time"
    "-----------------------------------------------------------"
    incr_save = math.floor(i * step_simu / sample_time)
    if incr_save > incr_save_old:
        print ("time="+repr(time_simu[i]))
        result_simu[incr_save, 0] = time_simu[i]
        result_simu[incr_save, 1] = Pair
        result_simu[incr_save, 2] = Compressor.E1.P
        result_simu[incr_save, 3] = Compressor.E2.P
        result_simu[incr_save, 4] = Compressor.E1.T
        result_simu[incr_save, 5] = Compressor.E2.T
        result_simu[incr_save, 6] = AirFilter.E2.P
        result_simu[incr_save, 7] = Compressor.F2.Qm
        result_simu[incr_save, 8] = N

    incr_save_old = incr_save

time2 = time.time()
print("Time for Simulation", repr(round((time2 - time1)*10)/10))
"-----------------------------------------------------------"
"PLOTS"
"-----------------------------------------------------------"
plt.figure(1)
plt.subplot(221)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 2],'r',result_simu[0:incr_save, 0],result_simu[0:incr_save, 3],'g')
plt.ylabel('Compressor Pressure [Pa]')
plt.subplot(222)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 4],'b',result_simu[0:incr_save, 0],result_simu[0:incr_save, 5],'r')
plt.ylabel('Compressor Temperature [K]')
plt.subplot(223)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 7])
plt.xlabel('time [s]')
plt.ylabel('Massic Flow [kg/s]')
plt.subplot(224)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 1],'r',result_simu[0:incr_save, 0],result_simu[0:incr_save, 6],'b')
plt.xlabel('time [s]')
plt.ylabel('Air Filter Pressure [Pa]')
plt.show()
