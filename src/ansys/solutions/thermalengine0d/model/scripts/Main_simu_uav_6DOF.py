# MAIN
import numpy as np
import matplotlib.pyplot as plt
import math
import time
from configparser import ConfigParser
from ansys.solutions.thermalengine0d.model.Library_Control_class import UavSupervisor, EMotorControl
from ansys.solutions.thermalengine0d.model.Library_Mechanics_class import Shaft_I, Propeller_Tf, Hydro1D_I, Hydro6D_I
from ansys.solutions.thermalengine0d.model.Library_Electrical_class import EMotor_Tf, LIBattery_C
from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import EffortM, FlowM, EffortE, FlowE, EffortMT, FlowMT
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolv

time1 = time.time()
"-----------------------------------------------------------"
"SIMULATION PARAMETER"
"-----------------------------------------------------------"
start_simu = 0
end_simu = 50
step_simu = 0.001
sample_time = 0.1
LastVal = (end_simu - start_simu) / step_simu

"-----------------------------------------------------------"
"SIMULATION CONFIG IMPORT"
"-----------------------------------------------------------"
config = ConfigParser()
config.read('ModelUAV_init.ini')
control = ConfigParser()
control.read('ModelUAV_control.ini')

"-----------------------------------------------------------"
"INIT"
"-----------------------------------------------------------"
N_ord = 0
N_act = 0
U = 0
alpha_mot = 21
I_ord = 0
I = 0
Vf = 0
Pw_on = 1
Pw_aux = 1000
TubeLength = 7.735

"Creation of vectors for saving / plots"
result_simu = np.zeros((int(LastVal+1 * step_simu / sample_time), 27))
time_simu = np.arange(1, LastVal+2)

"-----------------------------------------------------------"
"MODEL CREATION"
"-----------------------------------------------------------"
Electronic_section = UavSupervisor(N_act, N_ord, U)
Shaft = Shaft_I(EffortM(0), EffortM(0), N_act / 30 * math.pi)
Motor_control = EMotorControl(N_ord, N_act)
Motor = EMotor_Tf(EffortE(U), FlowM(N_act / 30 * math.pi), I_ord, alpha_mot)
Battery = LIBattery_C(FlowE(I))
Propeller = Propeller_Tf(FlowM(N_act / 30 * math.pi), FlowMT(Vf))
Hydro = Hydro1D_I(EffortMT(0))
Hydro_FreeWater = Hydro6D_I(EffortMT(0))

"-----------------------------------------------------------"
"MODEL PARAM"
"-----------------------------------------------------------"
Electronic_section.Param(25 / 7840)
Shaft.Param(0.003 * 30 / math.pi, 0, 0.98)
Motor_control.Param()
Motor.Param(eval(config.get('Motor_param','x_mot_efficiency')),eval(config.get('Motor_param','y_mot_efficiency')),eval(config.get('Motor_param','x_alpha')),eval(config.get('Motor_param','y_u_alpha')),eval(config.get('Motor_param','z_alpha_cor')))
Battery.Param(eval(config.get('Battery_param','x_capa')),eval(config.get('Battery_param','y_i')),eval(config.get('Battery_param','z_u')),eval(config.get('Battery_param','nelements')),eval(config.get('Battery_param','umin')))
Propeller.Param(eval(config.get('Hydro_param','rho_water')),eval(config.get('Propeller_param','kgear')),eval(config.get('Propeller_param','kwake')),eval(config.get('Propeller_param','ksuccion')),eval(config.get('Propeller_param','diam_prop')),eval(config.get('Propeller_param','front_rear_ratio')),eval(config.get('Propeller_param','eta_adaptation')),eval(config.get('Propeller_param','kt_x')),eval(config.get('Propeller_param','kt_y')),eval(config.get('Propeller_param','kq_x')),eval(config.get('Propeller_param','kq_y')))
Hydro.Param(eval(config.get('Hydro_param','mass')),eval(config.get('Hydro_param','diam')),eval(config.get('Hydro_param','length')),eval(config.get('Hydro_param','sm')),eval(config.get('Hydro_param','volume')),eval(config.get('Hydro_param','xg')),eval(config.get('Hydro_param','zg')),eval(config.get('Hydro_param','fins_s')),eval(config.get('Hydro_param','fins_e')),eval(config.get('Hydro_param','fins_c')),eval(config.get('Hydro_param','cmbeta')),eval(config.get('Hydro_param','cmw')),eval(config.get('Hydro_param','czbeta')),eval(config.get('Hydro_param','czw')),eval(config.get('Hydro_param','nu_water')),eval(config.get('Hydro_param','rho_water')))
Hydro_FreeWater.Param(eval(config.get('Hydro_param','mass')),eval(config.get('Hydro_param','diam')),eval(config.get('Hydro_param','length')),eval(config.get('Hydro_param','sm')),eval(config.get('Hydro_param','volume')),eval(config.get('Hydro_param','xg')), 0, eval(config.get('Hydro_param','zg')),eval(config.get('Hydro_param','fins_s')),eval(config.get('Hydro_param','fins_e')),eval(config.get('Hydro_param','fins_c')),eval(config.get('Hydro_param','nu_water')),eval(config.get('Hydro_param','rho_water')))

"-----------------------------------------------------------"
"SIMULATION"
"-----------------------------------------------------------"
time_simu[0]=start_simu
incr_save_old = 0
method = 'Euler'
X = 0
Y = 0
Z = 0
Phi = 0
Theta =0
Psi = 0
Acc_X = 0
V = 0

for i in range(1, int(LastVal+1)):
    time_simu[i] = i * step_simu + start_simu
    "function Nmot=f(time)"
    N_ord = interpolv(eval(control.get('Uav_control','x_time_Nord')), eval(control.get('Uav_control','y_Nord')), time_simu[i])

    "Hose Pipe"
    if eval(config.get('Hosepipe_param', 'length')) > 0:
        F_HosePipe = interpolv(eval(config.get('Hosepipe_param', 'x_f_hosepipe')), eval(config.get('Hosepipe_param', 'y_f_hosepipe')), X)
    else:
        F_HosePipe = 0

    "Electronic section"
    Electronic_section.N_ord = N_ord
    Electronic_section.U = Battery.Ee.U
    Electronic_section.Solve(step_simu, time_simu[i])

    "Shaft"
    Shaft.Em1 = Motor.Em
    Shaft.Em2 = Propeller.Em
    Shaft.Solve(step_simu, method)

    "Motor Control"
    Motor_control.N_ord = Electronic_section.Nmot_ord
    Motor_control.N_act = Shaft.Fm1.N
    Motor_control.Solve(step_simu, method)

    "Motor"
    Motor.Ee = Battery.Ee
    Motor.Fm = Shaft.Fm1
    Motor.I_ord = Motor_control.I_ord
    Motor.alpha_mot = Motor_control.alpha_mot
    Motor.Solve(Pw_on)

    "Battery"
    Battery.Fe.I = Motor.Fe.I + Pw_aux / Battery.Ee.U
    Battery.Solve(step_simu, Pw_on)
    Pw_on = Battery.PowerOn

    "Propeller"
    Propeller.Fm = Shaft.Fm2


    "Hydro 1D"
    if X <= TubeLength:
        Propeller.Fmt = Hydro.Fmt
        Propeller.Solve()
        Hydro.Emt = EffortMT(max(0, Propeller.Emt.Fx - F_HosePipe))
        Hydro.Solve(step_simu, method)
        X = Hydro.X
        Acc_X = Hydro.Acc_X
        V = Hydro.V

        "continuity between the 2 hydro models"
        Hydro_FreeWater.u = Hydro.V
        Hydro_FreeWater.X = Hydro.X

    else:
        Propeller.Fmt = Hydro_FreeWater.Fmt
        Propeller.Solve()
        Hydro_FreeWater.Rudders = Electronic_section.Rudders
        Hydro_FreeWater.Emt = EffortMT(max(0, Propeller.Emt.Fx - F_HosePipe), Propeller.Emt.Fy, Propeller.Emt.Fz, Propeller.Emt.Mx, Propeller.Emt.My, Propeller.Emt.Mz)
        Hydro_FreeWater.Solve(step_simu, method)
        X = Hydro_FreeWater.X
        Y = Hydro_FreeWater.Y
        Z = Hydro_FreeWater.Z
        Phi = Hydro_FreeWater.phi * 180 / math.pi
        Theta = Hydro_FreeWater.theta * 180 / math.pi
        Psi = Hydro_FreeWater.psi * 180 / math.pi
        Acc_X = Hydro_FreeWater.Acc_X
        V = Hydro_FreeWater.V



    "-----------------------------------------------------------"
    "Save results according to the defined sample time"
    "-----------------------------------------------------------"
    incr_save = math.floor(i * step_simu / sample_time)
    if incr_save > incr_save_old:
        print ("time="+repr(time_simu[i]))
        result_simu[incr_save, 0] = time_simu[i]
        result_simu[incr_save, 1] = Battery.Fe.I
        result_simu[incr_save, 2] = Battery.Ee.U
        result_simu[incr_save, 3] = Battery.Fe.Capacity / 3600
        result_simu[incr_save, 4] = Battery.Fe.Pwconsumed / 3600 / 1000
        result_simu[incr_save, 5] = Motor.Pwmot
        result_simu[incr_save, 6] = Shaft.Fm1.N
        result_simu[incr_save, 7] = Electronic_section.Nmot_ord
        result_simu[incr_save, 8] = Motor_control.Nmot_ord_PCU
        result_simu[incr_save, 9] = Acc_X
        result_simu[incr_save, 10] = V / 1852 * 3600
        result_simu[incr_save, 11] = Electronic_section.V_ord
        result_simu[incr_save, 12] = X
        result_simu[incr_save, 13] = Hydro.Pitch_eq
        result_simu[incr_save, 14] = Hydro.Beta_eq
        result_simu[incr_save, 15] = Motor_control.alpha_mot
        result_simu[incr_save, 16] = Motor_control.I_ord
        result_simu[incr_save, 17] = Motor_control.Flag_mot
        result_simu[incr_save, 18] = Y
        result_simu[incr_save, 19] = Z
        result_simu[incr_save, 20] = Phi
        result_simu[incr_save, 21] = Theta
        result_simu[incr_save, 22] = Psi
        result_simu[incr_save, 23] = Electronic_section.Rudders[0]
        result_simu[incr_save, 24] = Electronic_section.Rudders[1]
        result_simu[incr_save, 25] = Electronic_section.Rudders[2]
        result_simu[incr_save, 26] = Electronic_section.Rudders[3]

    incr_save_old = incr_save

time2 = time.time()
print("Time for Simulation", repr(round((time2 - time1)*10)/10))
"-----------------------------------------------------------"
"PLOTS"
"-----------------------------------------------------------"
plt.figure(1)
plt.subplot(231)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 7],'r',result_simu[0:incr_save, 0],result_simu[0:incr_save, 8],'g',result_simu[0:incr_save, 0],result_simu[0:incr_save, 6],'b')
plt.subplot(232)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 1],'b',result_simu[0:incr_save, 0],result_simu[0:incr_save, 2],'r')
plt.subplot(233)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 5])
plt.subplot(234)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 3],'b',result_simu[0:incr_save, 0],result_simu[0:incr_save, 4],'r')
plt.subplot(235)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 10],'b',result_simu[0:incr_save, 0],result_simu[0:incr_save, 11],'r')
plt.subplot(236)
plt.plot(result_simu[0:incr_save, 0],result_simu[0:incr_save, 9])
plt.figure(2)
plt.subplot(231)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 19])
plt.subplot(232)
plt.plot(result_simu[0:incr_save, 12], result_simu[0:incr_save, 18])
plt.subplot(233)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 20])
plt.subplot(234)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 21])
plt.subplot(235)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 22])
plt.subplot(236)
plt.plot(result_simu[0:incr_save, 0], result_simu[0:incr_save, 23],result_simu[0:incr_save, 0], result_simu[0:incr_save, 24],result_simu[0:incr_save, 0], result_simu[0:incr_save, 25],result_simu[0:incr_save, 0], result_simu[0:incr_save, 26])
plt.show()
