# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Backend of the first step."""

from ansys.saf.glow.solution import StepModel, StepSpec, transaction
from ansys.solutions.thermalengine0d.solution.config_step import ConfigStep
import numpy as np
import math
import time
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolv, interpolm
from ansys.solutions.thermalengine0d.model.Library_ThermoFluid_class import Compressor_Tf, Turbine_TF, Engine_Tf, PressureLosses_R, Volume_C, EffortSource, FlowSource
from ansys.solutions.thermalengine0d.model.scripts.Fluid_properties_class import FluidFuel
from ansys.solutions.thermalengine0d.model.Library_Mechanics_class import Shaft_I
from ansys.solutions.thermalengine0d.model.Library_Control_class import PI_control
from ansys.solutions.thermalengine0d.model.Library_Fluid_class import Injector_Sf
from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import EffortM, FlowM

class FirstStep(StepModel):
    """Step definition of the first step."""


    result: float = 0
    result_simu: dict = {}

    @transaction(self=StepSpec(upload=["result", "result_simu"]), config_step=StepSpec(download=["first_arg", "second_arg", "third_arg","control", "config", "x_N","y_N", "x_pps", "y_pps"]))
    def calculate(self, config_step: ConfigStep) -> None:


        time1 = time.time()
        "-----------------------------------------------------------"
        "SIMULATION PARAMETER"
        "-----------------------------------------------------------"
        start_simu = 0
        end_simu = config_step.first_arg
        step_simu = config_step.second_arg
        sample_time = config_step.third_arg
        LastVal = (end_simu - start_simu) / step_simu

        "-----------------------------------------------------------"
        "SIMULATION CONFIG IMPORT"
        "-----------------------------------------------------------"
        config = config_step.config
        control = config_step.control

        "-----------------------------------------------------------"
        "INIT"
        "-----------------------------------------------------------"
        Nturbo = eval(config['Integrators_init']['nturbo'])
        VNT = 0.7
        Pair = eval(config['Engine_param']['pair'])
        Tair = eval(config['Engine_param']['tair'])
        P0 = eval(control['Engine_control']['p0'])
        T0 = eval(control['Engine_control']['t0'])
        Fuel = FluidFuel(eval(config['Fuel_param']['ks']), eval(config['Fuel_param']['lhv']),
                         eval(config['Fuel_param']['hv']), eval(config['Fuel_param']['nc']),
                         eval(config['Fuel_param']['nh']))
        Ambient_Air = EffortSource(P0, T0)
        Flow_init = FlowSource(0, T0)

        "Creation of vectors for saving / plots"
        result_simu = np.zeros((int(LastVal + 1 * step_simu / sample_time), 15), dtype = float)
        time_simu = np.arange(1, LastVal + 2)

        "-----------------------------------------------------------"
        "MODEL CREATION"
        "-----------------------------------------------------------"
        AirFilter = PressureLosses_R(Ambient_Air.E, Ambient_Air.E)
        VolumeAirFilter = Volume_C(Flow_init.F, Flow_init.F)
        Compressor = Compressor_Tf(Ambient_Air.E, Ambient_Air.E, FlowM(Nturbo / 30 * math.pi))
        VolumeCompr = Volume_C(Flow_init.F, Flow_init.F)
        Intake = PressureLosses_R(Ambient_Air.E, Ambient_Air.E)
        VolumeIntake = Volume_C(Flow_init.F, Flow_init.F)
        Injector = Injector_Sf(0, Fuel.LHV)
        Engine = Engine_Tf(Ambient_Air.E, Ambient_Air.E, FlowM(0), Injector, Fuel, Pair, Tair)
        VolumeTurb = Volume_C(Flow_init.F, Flow_init.F, P0, T0, Fuel.nC, Fuel.nH, Engine.FAR)
        Turbine = Turbine_TF(Ambient_Air.E, Ambient_Air.E, FlowM(Nturbo / 30 * math.pi), VNT, Fuel.nC, Fuel.nH,
                             Engine.FAR)
        VolumeExhaust = Volume_C(Flow_init.F, Flow_init.F, P0, T0, Fuel.nC, Fuel.nH, Engine.FAR)
        Exhaust = PressureLosses_R(Ambient_Air.E, Ambient_Air.E)
        TurboShaft = Shaft_I(EffortM(0), EffortM(0), Nturbo / 30 * math.pi)
        PI_VNT = PI_control(P0, P0)

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
        Intake.Param(eval(config['Intake_param']['k_pl_intake']))
        VolumeIntake.Param(eval(config['Intake_param']['vol_intake'])+eval(config['Intercooler_param']['vol_ic']))
        Injector.Param(eval(control['Engine_ECU']['x_ne']), eval(control['Engine_ECU']['y_pps_qinj']),
                       eval(control['Engine_ECU']['z_qinj']))
        Engine.Param(eval(config['Engine_param']['vcyl']), eval(config['Engine_param']['x_ne']),
                     eval(config['Engine_param']['y_rho1rho2']),
                     eval(config['Engine_param']['y_etavol_overall']), eval(config['Engine_param']['z_etavol']),
                     eval(config['Engine_param']['z_etaind']), eval(config['Engine_param']['z_etacomb']))
        VolumeTurb.Param(eval(config['Outlet_param']['vol_om'])+eval(config['Turbine_param']['vol_turbine']))
        Turbine.Param(eval(config['Turbine_param']['preft']), eval(config['Turbine_param']['treft']),
                      eval(config['Turbine_param']['x_pr']), eval(config['Turbine_param']['y_vntposition']),
                      eval(config['Turbine_param']['z_flowt_cor']), eval(config['Turbine_param']['z_eta_turb'])*1.12)
        VolumeExhaust.Param(eval(config['Exhaust_param']['vol_ex']))
        Exhaust.Param(eval(config['Exhaust_param']['k_pl_exhaust']))
        TurboShaft.Param(eval(config['Compr_param']['inertia'])+eval(config['Turbine_param']['inertia']), 1000)
        PI_VNT.Param(eval(control['Engine_ECU']['kp']), eval(control['Engine_ECU']['ki']), eval(control['Engine_ECU']['vnt_min']), eval(control['Engine_ECU']['vnt_max']))

        "-----------------------------------------------------------"
        "SIMULATION"
        "-----------------------------------------------------------"
        time_simu[0] = start_simu
        incr_save_old = 0
        method = 'Trapezoidal'

        for i in range(1, int(LastVal + 1)):
            time_simu[i] = i * step_simu + start_simu
            "Pedal position=f(time_simu)"
            N = interpolv(eval(config_step.x_N),
                          eval(config_step.y_N), time_simu[i])
            pps = interpolv(eval(config_step.x_pps),
                            eval(config_step.y_pps), time_simu[i])
            P1E_Ord = interpolm(eval(control['Engine_ECU']['y_pps_qinj']), eval(control['Engine_ECU']['x_ne']),
                                eval(control['Engine_ECU']['z_p1e_ord']), pps, N)
            Kp_VNT = interpolv(eval(control['Engine_ECU']['x_epsilon_kp']),
                            eval(control['Engine_ECU']['y_kp']), P1E_Ord - Engine.E1.P)

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
            Compressor.Fm = TurboShaft.Fm1
            Compressor.Solve()
            VolumeCompr.F1 = Compressor.F2
            VolumeCompr.F2 = Intake.F1
            VolumeCompr.Solve(step_simu, method)

            "Engine Intake"
            Intake.E1 = VolumeCompr.E2
            Intake.E2 = VolumeIntake.E1
            Intake.Solve()
            VolumeIntake.F1 = Intake.F2
            VolumeIntake.F2 = Engine.F1
            VolumeIntake.Solve(step_simu, method)

            "Engine bloc"
            Engine.Fm = FlowM(N / 30 * math.pi)
            Engine.E1 = VolumeIntake.E2
            Engine.E1.T = 273+40
            Engine.E2 = VolumeTurb.E1
            Injector.Solve(pps, Engine.Fm)
            Engine.Solve()


            "Turbine"
            VolumeTurb.F1 = Engine.F2
            VolumeTurb.F2 = Turbine.F1
            VolumeTurb.FAR = Engine.FAR
            VolumeTurb.Solve(step_simu, method)
            Turbine.E1 = VolumeTurb.E2
            Turbine.E2 = Exhaust.E1
            Turbine.FAR = Engine.FAR
            Turbine.Fm = TurboShaft.Fm2
            Turbine.VNT = PI_VNT.y
            Turbine.Solve()

            "Exhaust"
            VolumeExhaust.F1 = Turbine.F2
            VolumeExhaust.F2 = Exhaust.F1
            VolumeExhaust.FAR = Engine.FAR
            VolumeExhaust.Solve(step_simu, method)
            Exhaust.E1 = VolumeExhaust.E2
            Exhaust.E2 = Ambient_Air.E
            Exhaust.Solve()

            "Turbo Shaft"
            TurboShaft.Em1 = Compressor.Em
            TurboShaft.Em2 = Turbine.Em
            TurboShaft.Solve(step_simu, method)

            "VNT Control"
            PI_VNT.x_Ord = P1E_Ord
            PI_VNT.x_Act = Engine.E1.P
            PI_VNT.Kp = Kp_VNT*0.25
            PI_VNT.Solve(step_simu, method)

            "-----------------------------------------------------------"
            "Save results according to the defined sample time"
            "-----------------------------------------------------------"
            incr_save = math.floor(i * step_simu / sample_time)
            if incr_save > incr_save_old:
                result_simu[incr_save, 0] = time_simu[i]
                result_simu[incr_save, 1] = Engine.Em.Tq
                result_simu[incr_save, 2] = Engine.F1.Qm * -1
                result_simu[incr_save, 3] = Engine.F2.Qm
                result_simu[incr_save, 4] = Engine.FAR
                result_simu[incr_save, 5] = Engine.E1.P
                result_simu[incr_save, 6] = Engine.E2.P
                result_simu[incr_save, 7] = Engine.E1.T
                result_simu[incr_save, 8] = Turbine.E1.T
                result_simu[incr_save, 9] = Turbine.E2.T
                result_simu[incr_save, 10] = Engine.Fm.N
                result_simu[incr_save, 11] = TurboShaft.Fm1.N
                result_simu[incr_save, 12] = PI_VNT.y
                result_simu[incr_save, 13] = PI_VNT.x_Ord
                result_simu[incr_save, 14] = Compressor.E2.T

            incr_save_old = incr_save

        time2 = time.time()
        self.result = round((time2 - time1)*10)/10

        self.result_simu['time'] = list(result_simu[0:incr_save, 0])
        self.result_simu['TqE'] = list(result_simu[0:incr_save, 1])
        self.result_simu['Qm1E'] = list(result_simu[0:incr_save, 2])
        self.result_simu['Qm2E'] = list(result_simu[0:incr_save, 3])
        self.result_simu['FAR'] = list(result_simu[0:incr_save, 4])
        self.result_simu['P1E'] = list(result_simu[0:incr_save, 5])
        self.result_simu['P2E'] = list(result_simu[0:incr_save, 6])
        self.result_simu['T1E'] = list(result_simu[0:incr_save, 7])
        self.result_simu['T1T'] = list(result_simu[0:incr_save, 8])
        self.result_simu['T2T'] = list(result_simu[0:incr_save, 9])
        self.result_simu['NE'] = list(result_simu[0:incr_save, 10])
        self.result_simu['NT'] = list(result_simu[0:incr_save, 11])
        self.result_simu['VNT_act'] = list(result_simu[0:incr_save, 12])
        self.result_simu['P1E_ord'] = list(result_simu[0:incr_save, 13])
        self.result_simu['T2C'] = list(result_simu[0:incr_save, 14])








