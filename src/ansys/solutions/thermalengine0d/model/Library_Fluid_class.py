# Fluid library
# Contains:
#   - Injector (Sf)


from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import FlowF, EffortF, FlowE
from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import EffortTH
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolm, interpolv
from ansys.solutions.thermalengine0d.model.scripts.Solver import Integrator

"------------------------------------------------------------------------"
"Injector (Sf element)"
"------------------------------------------------------------------------"

class Injector_Sf:
    def __init__(self, Qm, LHV):
        self.Qm = Qm
        self.LHV=LHV
        self.Qmh = self.Qm*self.LHV
        self.F = FlowF(self.Qm, self.Qmh)

    def Param(self, x_NE, y_pps_Qinj,z_Qinj):
        self. x_NE = x_NE
        self.y_pps_Qinj = y_pps_Qinj
        self.z_Qinj = z_Qinj

    def Solve(self,PedalPosition,Fm):
        self.Fm = Fm
        self.Qm = interpolm(self.y_pps_Qinj, self.x_NE, self.z_Qinj, PedalPosition, self.Fm.N)
        self.Qmh = self.Qm*self.LHV
        self.F = FlowF(self.Qm, self.Qmh)


"------------------------------------------------------------------------"
"Source of Flow (Sf element)"
"------------------------------------------------------------------------"
class FlowSourceFluid:
    def __init__(self, Qm=0, h=0, Phi=0):
        self.Qm = Qm
        self.h = h
        self.Qmh = Qm * self.h
        self.Phi = Phi
        self.F = FlowF(self.Qm, self.Qmh, self.Phi)

    def Param(self, Qm, h, Phi=0):
        self.Qm = Qm
        self.h = h
        self.Qmh = Qm * self.h
        self.Phi = Phi
        self.F = FlowF(self.Qm, self.Qmh, self.Phi)

    def Solve(self, dt, method='Euler'):
        self.dt = dt
        self.method = method
        self.F = FlowF(self.Qm, self.Qmh, self.Phi)

"------------------------------------------------------------------------"
"Electric Pump with Heating (Tf element)"
"------------------------------------------------------------------------"
class PumpFluid:
    def __init__(self, E1=0, E2=0, Ee=0, I_ord=0):
        if E1 == 0:
            self.E1 = EffortF(1e5, 293)
        else:
            self.E1 = E1
        if E1 == 0:
            self.E2 = EffortF(1e5, 293)
        else:
            self.E2 = E2
        self.Ee = Ee
        self.I_ord = I_ord
        self.I = 0
        self.Fe = FlowE(self.I)
        self.Qm = 0
        self.Qmh = 0
        self.F1 = FlowF(-self.Qm, -self.Qmh)
        self.F2 = FlowF(self.Qm, self.Qmh)


    def Param(self, x_pump, z_flow, Rho, Cp, deltaT_heating = 0):
        self.x_pump = x_pump
        self.z_flow = z_flow
        self.Rho = Rho
        self.Cp = Cp
        self.deltaT_heating = deltaT_heating

    def Solve(self, dt, method='Euler'):
        self.dt = dt
        self.method = method

        self.I = self.I_ord
        "massic flow calculation"
        self.Qv = interpolv(self.x_pump, self.z_flow, self.I)
        self.Qm = self.Qv * self.Rho

        "Outlet temperature calculation"
        if self.Qm <= 0:
            self.T2 = self.E1.T
        else:
            self.T2 = self.E1.T + self.deltaT_heating


        "flow port creation"
        self.F1 = FlowF(-self.Qm, -self.Qm*self.E1.T*self.Cp)
        self.F2 = FlowF(self.Qm, self.Qm*self.T2*self.Cp)

        self.Fe = FlowE(self.I)



"------------------------------------------------------------------------"
"Non adiabatic Volume function (C element)"
"------------------------------------------------------------------------"
class VolumeFluid_C:
    def __init__(self, F1=0, F2=0, Fth=0):
        if F1 == 0:
            self.F1 = FlowF(0, 0)
        else:
            self.F1 = F1
        if F2 == 0:
            self.F2 = FlowF(0, 0)
        else:
            self.F2 = F2
        if Fth == 0:
            self.Fth = FlowF(0, 0)
        else:
            self.Fth = Fth

        self.delta_Qm = 0
        self.deltaT = 0


    def Param(self, Volume, Cp, Rho, BulkModulus, P0=1e5, T0=298):
        self.Volume = Volume
        self.Cp = Cp
        self.Rho = Rho
        self.BulkModulus = BulkModulus
        self.m = self.Volume * self.Rho
        self.P = P0
        self.T = T0
        self.E1 = EffortF(self.P, self.T)
        self.E2 = self.E1
        self.Eth = EffortTH(self.T)

    def Solve(self, dt, method='Euler'):

        "mass balance"
        self.delta_Qm_prev = self.delta_Qm
        self.delta_Qm = self.F1.Qm + self.F2.Qm
        self.m = Integrator(self.m, self.delta_Qm, dt, self.delta_Qm_prev, method)

        "energy balance"
        delta_Qh = self.F1.Qmh + self.F2.Qmh + self.Fth.Phi
        self.deltaT_prev = self.deltaT
        self.deltaT = (delta_Qh - self.Cp * self.T * self.delta_Qm) / self.m / self.Cp
        self.T = Integrator(self.T, self.deltaT, dt, self.deltaT_prev, method)
        self.P = Integrator(self.P, self.delta_Qm * self.BulkModulus / self.Volume / self.Rho, dt, self.delta_Qm_prev * self.BulkModulus / self.Volume / self.Rho, method)

        "effort port creation"
        self.E1 = EffortF(self.P, self.T)
        self.E2 = self.E1
        self.Eth = EffortTH(self.T)

"------------------------------------------------------------------------"
"Non adiabatic Volume function (C element) with external heating"
"------------------------------------------------------------------------"
class VolumeFluid_C_2HEX:
    def __init__(self, F1=0, F2=0, Fth1=0, Fth2=0):
        if F1 == 0:
            self.F1 = FlowF(0, 0)
        else:
            self.F1 = F1
        if F2 == 0:
            self.F2 = FlowF(0, 0)
        else:
            self.F2 = F2
        if Fth1 == 0:
            self.Fth1 = FlowF(0, 0)
        else:
            self.Fth1 = Fth1
        if Fth2 == 0:
            self.Fth2 = FlowF(0, 0)
        else:
            self.Fth2 = Fth2
        self.delta_Qm = 0
        self.deltaT = 0


    def Param(self, Volume, Cp, Rho, BulkModulus, P0=1e5, T0=298):
        self.Volume = Volume
        self.Cp = Cp
        self.Rho = Rho
        self.BulkModulus = BulkModulus
        self.m = self.Volume * self.Rho
        self.P = P0
        self.T = T0
        self.E1 = EffortF(self.P, self.T)
        self.E2 = self.E1
        self.Eth1 = EffortTH(self.T)
        self.Eth2 = EffortTH(self.T)

    def Solve(self, dt, method='Euler'):

        "mass balance"
        self.delta_Qm_prev = self.delta_Qm
        self.delta_Qm = self.F1.Qm + self.F2.Qm
        self.m = Integrator(self.m, self.delta_Qm, dt, self.delta_Qm_prev, method)

        "energy balance"
        delta_Qh = self.F1.Qmh + self.F2.Qmh + self.Fth1.Phi + self.Fth2.Phi
        self.deltaT_prev = self.deltaT
        self.deltaT = (delta_Qh - self.Cp * self.T * self.delta_Qm) / self.m / self.Cp
        self.T = Integrator(self.T, self.deltaT, dt, self.deltaT_prev, method)
        self.P = Integrator(self.P, self.delta_Qm * self.BulkModulus / self.Volume / self.Rho, dt, self.delta_Qm_prev * self.BulkModulus / self.Volume / self.Rho, method)

        "effort port creation"
        self.E1 = EffortF(self.P, self.T)
        self.E2 = self.E1
        self.Eth1 = EffortTH(self.T)
        self.Eth2 = EffortTH(self.T)