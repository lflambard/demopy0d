# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Backend of the first step."""

from ansys.saf.glow.solution import StepModel, StepSpec, transaction
import numpy as np
import math
import time
from ansys.solutions.thermalengine0d.solution.Data_treatment import interpolv
from ansys.solutions.thermalengine0d.solution.Library_ThermoFluid_class import Compressor_Tf, Turbine_TF, Engine_Tf, PressureLosses_R, Volume_C, EffortSource, FlowSource
from ansys.solutions.thermalengine0d.solution.Fluid_properties_class import FluidFuel
from ansys.solutions.thermalengine0d.solution.Library_Mechanics_class import Shaft_I
from ansys.solutions.thermalengine0d.solution.Library_Control_class import PI_control
from ansys.solutions.thermalengine0d.solution.Library_Fluid_class import Injector_Sf
from ansys.solutions.thermalengine0d.solution.EffortFlowPort_class import EffortM, FlowM

class FirstStep(StepModel):
    """Step definition of the first step."""

    first_arg: float = 0
    second_arg: float = 0
    result: float = 0


    @transaction(self=StepSpec(upload=["result"], download=["first_arg", "second_arg"]))
    def calculate(self) -> None:


        time1 = time.time()
        "-----------------------------------------------------------"
        "SIMULATION PARAMETER"
        "-----------------------------------------------------------"
        start_simu = 0.1
        end_simu = self.first_arg
        step_simu = self.second_arg
        sample_time = 0.01
        LastVal = (end_simu - start_simu) / step_simu


        "-----------------------------------------------------------"
        "SIMULATION CONFIG IMPORT"
        "-----------------------------------------------------------"
        from configparser import ConfigParser
        config = ConfigParser()
        config.read('src/ansys/solutions/thermalengine0d/solution/Model_init.ini')
        control = ConfigParser()
        control.read('src/ansys/solutions/thermalengine0d/solution/Model_control.ini')


        "-----------------------------------------------------------"
        "INIT"
        "-----------------------------------------------------------"
        VT = config.getfloat('Integrators_init', 'VT')
        Nturbo = config.getfloat('Integrators_init', 'Nturbo')
        VNT = config.getfloat('Turbine_param', 'VNT')
        Pair = config.getfloat('Integrators_init', 'Pair')
        Tair = config.getfloat('Integrators_init', 'Tair')
        P0 = config.getfloat('Integrators_init', 'P0')
        T0 = config.getfloat('Integrators_init', 'T0')
        Fuel = FluidFuel(config.getfloat('Fuel_param', 'Ks'), config.getfloat('Fuel_param', 'LHV'),
                         config.getfloat('Fuel_param', 'Hv'), config.getfloat('Fuel_param', 'nC'),
                         config.getfloat('Fuel_param', 'nH'))
        Ambient_Air = EffortSource(P0, T0)
        Flow_init = FlowSource(0, T0)

        "Creation of vectors for saving / plots"
        result_simu = np.zeros((int(LastVal + 1 * step_simu / sample_time), 14))
        time_simu = np.arange(1, LastVal + 2)

        "-----------------------------------------------------------"
        "MODEL CREATION"
        "-----------------------------------------------------------"
        Compressor = Compressor_Tf(Ambient_Air.E, Ambient_Air.E, FlowM(Nturbo / 30 * math.pi))
        VolumeCompr = Volume_C(Flow_init.F, Flow_init.F)
        Intake = PressureLosses_R(Ambient_Air.E, Ambient_Air.E)
        VolumeIntake = Volume_C(Flow_init.F, Flow_init.F)
        Injector = Injector_Sf(0, Fuel.LHV)
        Engine = Engine_Tf(Ambient_Air.E, Ambient_Air.E, FlowM(0), Injector, Fuel, Pair, Tair)
        VolumeExhaust = Volume_C(Flow_init.F, Flow_init.F, P0, T0, Fuel.nC, Fuel.nH, Engine.FAR)
        Exhaust = PressureLosses_R(Ambient_Air.E, Ambient_Air.E)
        VolumeTurb = Volume_C(Flow_init.F, Flow_init.F, P0, T0, Fuel.nC, Fuel.nH, Engine.FAR)
        Turbine = Turbine_TF(Ambient_Air.E, Ambient_Air.E, FlowM(Nturbo / 30 * math.pi), VNT, Fuel.nC, Fuel.nH,
                             Engine.FAR)
        TurboShaft = Shaft_I(EffortM(0), EffortM(0), Nturbo / 30 * math.pi)
        PI_VNT = PI_control(P0, P0)

        "-----------------------------------------------------------"
        "MODEL PARAM"
        "-----------------------------------------------------------"
        Compressor.Param(config.getfloat('Compr_param', 'Prefc'), config.getfloat('Compr_param', 'Trefc'),
                         eval(config.get('Compr_param', 'x_NC')), eval(config.get('Compr_param', 'surge_PR')),
                         eval(config.get('Compr_param', 'y_margin')), eval(config.get('Compr_param', 'z_flow_cor')),
                         eval(config.get('Compr_param', 'z_eta_Comp')))
        VolumeCompr.Param(VT)
        Intake.Param(config.getfloat('Intake_param', 'K_pl_intake'))
        VolumeIntake.Param(VT)
        Injector.Param(eval(config.get('Engine_param', 'x_NE')), eval(config.get('Engine_param', 'y_pps_Qinj')),
                       eval(config.get('Engine_param', 'z_Qinj')))
        Engine.Param(config.getfloat('Engine_param', 'Vcyl'), eval(config.get('Engine_param', 'x_NE')),
                     eval(config.get('Engine_param', 'y_rho1rho2')),
                     eval(config.get('Engine_param', 'y_etavol_overall')), eval(config.get('Engine_param', 'z_etavol')),
                     eval(config.get('Engine_param', 'z_etaind')), eval(config.get('Engine_param', 'z_etacomb')))
        VolumeExhaust.Param(VT)
        Exhaust.Param(config.getfloat('Exhaust_param', 'K_pl_exhaust'))
        VolumeTurb.Param(VT)
        Turbine.Param(config.getfloat('Turbine_param', 'Preft'), config.getfloat('Turbine_param', 'Treft'),
                      eval(config.get('Turbine_param', 'x_PR')), eval(config.get('Turbine_param', 'y_VNTposition')),
                      eval(config.get('Turbine_param', 'z_flowT_cor')), eval(config.get('Turbine_param', 'z_eta_Turb')))
        TurboShaft.Param(0.000009, 1000)
        PI_VNT.Param(-5e-5, 8, 0.17, 1)

        "-----------------------------------------------------------"
        "SIMULATION"
        "-----------------------------------------------------------"
        time_simu[0] = start_simu
        incr_save_old = 0

        for i in range(1, int(LastVal + 1)):
            time_simu[i] = i * step_simu + start_simu
            "Pedal position=f(time_simu)"
            N = interpolv(eval(control.get('Engine_control', 'x_time_Nord')),
                          eval(control.get('Engine_control', 'y_Nord')), time_simu[i])
            pps = interpolv(eval(control.get('Engine_control', 'x_time_pps')),
                            eval(control.get('Engine_control', 'y_pps')), time_simu[i])
            P1E_Ord = interpolv(eval(control.get('Engine_control', 'x_time_pps')),
                                eval(control.get('Engine_control', 'y_P1E_Ord')), time_simu[i])

            "Compressor"
            Compressor.E1 = Ambient_Air.E
            Compressor.E2 = VolumeCompr.E1
            Compressor.Fm = TurboShaft.Fm1
            Compressor.Solve()
            VolumeCompr.F1 = Compressor.F2
            VolumeCompr.F2 = Intake.F1
            VolumeCompr.Solve(step_simu)

            "Engine Intake"
            Intake.E1 = VolumeCompr.E2
            Intake.E2 = VolumeIntake.E1
            Intake.Solve()
            VolumeIntake.F1 = Intake.F2
            VolumeIntake.F2 = Engine.F1
            VolumeIntake.Solve(step_simu)

            "Engine bloc"
            Engine.Fm = FlowM(N / 30 * math.pi)
            Engine.E1 = VolumeIntake.E2
            Engine.E2 = VolumeExhaust.E1
            Injector.Solve(pps, Engine.Fm)
            Engine.Solve()

            "Engine Exhaust"
            VolumeExhaust.F1 = Engine.F2
            VolumeExhaust.F2 = Exhaust.F1
            VolumeExhaust.FAR = Engine.FAR
            VolumeExhaust.Solve(step_simu)
            Exhaust.E1 = VolumeExhaust.E2
            Exhaust.E2 = VolumeTurb.E1
            Exhaust.Solve()

            "Turbine"
            VolumeTurb.F1 = Exhaust.F2
            VolumeTurb.F2 = Turbine.F1
            VolumeTurb.FAR = Engine.FAR
            VolumeTurb.Solve(step_simu)
            Turbine.E1 = VolumeTurb.E2
            Turbine.E2 = Ambient_Air.E
            Turbine.FAR = Engine.FAR
            Turbine.Fm = TurboShaft.Fm2
            Turbine.VNT = PI_VNT.y
            Turbine.Solve()

            "Turbo Shaft"
            TurboShaft.Em1 = Compressor.Em
            TurboShaft.Em2 = Turbine.Em
            TurboShaft.Solve(step_simu)

            "VNT Control"
            PI_VNT.x_Ord = P1E_Ord
            PI_VNT.x_Act = Engine.E1.P
            PI_VNT.Solve(step_simu)

            "-----------------------------------------------------------"
            "Save results according to the defined sample time"
            "-----------------------------------------------------------"
            incr_save = math.floor(i * step_simu / sample_time)
            if incr_save > incr_save_old:
                print("time=" + repr(time_simu[i]))
                result_simu[incr_save, 0] = time_simu[i]
                result_simu[incr_save, 1] = Engine.Em.Tq
                result_simu[incr_save, 2] = Engine.F1.Qm
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

            incr_save_old = incr_save

            time2 = time.time()

            self.result = round((time2 - time1)*10)/10

            self.result_simu = result_simu









