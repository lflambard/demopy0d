# MAIN
import numpy as np
import matplotlib.pyplot as plt
import math
from ansys.solutions.thermalengine0d.model.scripts.CombustionFunctions import CrankAngle, PcylSimple, Piston
from ansys.solutions.thermalengine0d.model.scripts.Solver import Integrator_Euler

"-----------------------------------------------------------"
"SIMULATION PARAMETER"
"-----------------------------------------------------------"
start_simu = 0
end_simu = 0.25
step_simu = 0.000001
sample_time = 0.0001
LastVal = (end_simu - start_simu) / step_simu

"-----------------------------------------------------------"
"SIMULATION CONFIG IMPORT"
"-----------------------------------------------------------"
Bore = 85
Stroke = 92
ConnectingRod = 143
Mass = 0.2
CompRatio = 18
KcombCor = 7.277

"-----------------------------------------------------------"
"INIT"
"-----------------------------------------------------------"
N = 1000
nCyl = 1
VBQ0 = 0    #initial position of the CrankShaft
P1_init = 1.5e5
P2_init = 2e5
Pmi = 60e5
Tqe_mean = 0

"Creation of vectors for saving / plots"
time_simu = np.arange(1, LastVal+2)
result_simu = np.zeros((int(LastVal+1 * step_simu / sample_time), 5))


"-----------------------------------------------------------"
"MODEL CREATION"
"-----------------------------------------------------------"
VBQ = CrankAngle(N * math.pi / 30)
PistonChamber = Piston(P1_init, N, VBQ0)
Combustion = PcylSimple(P1_init, P2_init, Pmi, VBQ0, PistonChamber.VolCyl)

"-----------------------------------------------------------"
"MODEL PARAM"
"-----------------------------------------------------------"
VBQ.Param(VBQ0, nCyl)
PistonChamber.Param(Bore, Stroke, ConnectingRod, Mass, CompRatio)
Combustion.Param(Bore, Stroke, ConnectingRod, CompRatio, KcombCor)

"-----------------------------------------------------------"
"SIMULATION"
"-----------------------------------------------------------"
time_simu[0] = start_simu
incr_save_old = 0

for i in range(1, int(LastVal+1)):
    time_simu[i] = i * step_simu + start_simu

    "Crank Angle"
    VBQ.time = time_simu[i]
    VBQ.Solve(VBQ.time)

    "Piston"
    PistonChamber.Pcyl = Combustion.Pcyl
    PistonChamber.N = N
    PistonChamber.CrankAngle = VBQ.CrankAngle
    PistonChamber.Solve()

    "Combustion"
    Combustion.VolCyl = PistonChamber.VolCyl
    Combustion.P1 = P1_init
    Combustion.P2 = P2_init
    Combustion.Pmi = Pmi
    Combustion.CrankAngle = VBQ.CrankAngle
    Combustion.Solve()

    "Mean value for Indicated Engine Torque"
    Tqe_mean = Integrator_Euler(Tqe_mean, PistonChamber.Tq * N / 120, step_simu)
    Tqi_mean = Tqe_mean + (P2_init - P1_init) * (Combustion.CompRatio * Combustion.DeadVol - Combustion.DeadVol) / 4 / math.pi
    Tqi_ref = Pmi * (Combustion.CompRatio * Combustion.DeadVol - Combustion.DeadVol) / 4 / math.pi

    "-----------------------------------------------------------"
    "Save results according to the defined sample time"
    "-----------------------------------------------------------"
    incr_save = math.floor(i * step_simu / sample_time)
    if incr_save > incr_save_old:
        print("time=" + repr(time_simu[i]))
        result_simu[incr_save, 0] = time_simu[i]
        result_simu[incr_save, 1] = VBQ.CrankAngle
        result_simu[incr_save, 2] = PistonChamber.VolCyl
        result_simu[incr_save, 3] = Combustion.Pcyl
        result_simu[incr_save, 4] = PistonChamber.Tq
    incr_save_old = incr_save

    if VBQ.CrankAngle >= 719:
        break


"-----------------------------------------------------------"
"PLOTS"
"-----------------------------------------------------------"
print(Tqi_mean)
print(Tqi_ref)
print(Tqi_ref/Tqi_mean)
plt.figure(1)
plt.subplot(221)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 1])
plt.subplot(222)
plt.plot(result_simu[0:incr_save, 1], result_simu[0:incr_save, 3])
plt.subplot(223)
plt.plot(result_simu[0:incr_save, 1], result_simu[0:incr_save, 4])
plt.subplot(224)
plt.plot(result_simu[0:incr_save, 2], result_simu[0:incr_save, 3])
plt.show()