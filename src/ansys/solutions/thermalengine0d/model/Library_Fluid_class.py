# Fluid library
# Contains:
#   - Injector (Sf)


from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import FlowF, EffortF
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolm
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
    def __init__(self, Qm, h, Phi=0):
        self.Qm = Qm
        self.h = h
        self.Qmh = Qm * self.h
        self.Phi = Phi
        self.F = FlowF(self.Qm, self.Qmh, self.Phi)

"------------------------------------------------------------------------"
"(Non) adiabatic Volume function (C element)"
"------------------------------------------------------------------------"
class VolumeFluid_C:
    def __init__(self, F1, F2, Phi=0, P0=1e5, T0=298):
        self.F1 = F1
        self.F2 = F2
        self.Phi = Phi
        self.P = P0
        self.T = T0
        self.delta_Qm = 0
        self.deltaT = 0
        self.E1 = EffortF(self.P, self.T)
        self.E2 = self.E1

    def Param(self, Volume, Cp, Rho, BulkModulus):
        self.Volume = Volume
        self.Cp = Cp
        self.Rho = Rho
        self.BulkModulus = BulkModulus
        self.m = self.Volume * self.Rho

    def Solve(self, dt, method='Euler'):

        "mass balance"
        self.delta_Qm_prev = self.delta_Qm
        self.delta_Qm = self.F1.Qm + self.F2.Qm
        self.m = Integrator(self.m, self.delta_Qm, dt, self.delta_Qm_prev, method)

        "energy balance"
        delta_Qh = self.F1.Qmh + self.F2.Qmh + self.Phi
        self.deltaT_prev = self.deltaT
        self.deltaT = (delta_Qh - self.Cp * self.T * self.delta_Qm) / self.m / self.Cp
        self.T = Integrator(self.T, self.deltaT, dt, self.deltaT_prev, method)
        self.P = self.P

        "effort port creation"
        self.E1 = EffortF(self.P, self.T)
        self.E2 = self.E1

