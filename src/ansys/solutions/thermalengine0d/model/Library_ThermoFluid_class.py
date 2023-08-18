# Thermo Fluid library
# Contains:
#   - Pressure losses element (R)
#   - Volume element (C)
#   - Compressor element (Tf)
#   - Turbine element (Tf)
#   - Engine element (Tf)
#   - Source of Effort (Se)
#   - Source of Flow (Sf)
from ansys.solutions.thermalengine0d.model.scripts.Fluid_properties_class import FluidBGM, FluidFuel
from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import EffortTF, FlowTF, EffortM, FlowM
from ansys.solutions.thermalengine0d.model.scripts.Solver import Integrator_Euler, Integrator
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolm, interpolv

"------------------------------------------------------------------------"
"Source of Effort (Se element)"
"------------------------------------------------------------------------"


class EffortSource(FluidBGM):
    def __init__(self, P, T, nC=10.8, nH=18.7, FAR=0):
        FluidBGM.__init__(self, nC, nH, FAR, T)
        self.P = P
        self.T = T
        self.E = EffortTF(self.P, self.T, self.h, self.u, self.cp, self.gamma, self.R, FAR)


"------------------------------------------------------------------------"
"Source of Flow (Sf element)"
"------------------------------------------------------------------------"


class FlowSource(FluidBGM):
    def __init__(self, Qm, T, nC=10.8, nH=18.7, FAR=0):
        FluidBGM.__init__(self, nC, nH, FAR, T)
        self.Qm = Qm
        self.T = T
        self.Qmh = Qm * self.h
        self.F = FlowTF(self.Qm, self.Qmh)


"------------------------------------------------------------------------"
"Pressure losses component (R element)"
"------------------------------------------------------------------------"


class PressureLosses_R:
    def __init__(self, E1, E2):
        self.E1 = E1
        self.E2 = E2
        self.Qm = 0
        self.Qmh = self.Qm * self.E1.h
        self.F1 = FlowTF(-self.Qm, -self.Qmh)
        self.F2 = FlowTF(self.Qm, self.Qmh)

    def Param(self,K_PressureLosses):
        self.K_PressureLosses = K_PressureLosses

    def Solve(self):
        if (self.E1.P - self.E2.P) >= 0:
            self.Qm = (self.E1.P / self.E1.T / self.E1.R) * self.K_PressureLosses * (self.E1.P - self.E2.P) ** 0.5
            self.Qmh = self.Qm * self.E1.h
        else:
            self.Qm = -(self.E2.P / self.E2.T / self.E2.R) * self.K_PressureLosses * (self.E2.P - self.E1.P) ** 0.5
            self.Qmh = self.Qm * self.E2.h

        "flow port creation"
        self.F1 = FlowTF(-self.Qm, -self.Qmh)
        self.F2 = FlowTF(self.Qm, self.Qmh)


"------------------------------------------------------------------------"
"Volume function (C element)"
"------------------------------------------------------------------------"


class Volume_C:
    def __init__(self, F1, F2, P0=1e5, T0=298, nC=10.8, nH=18.7, FAR=0):
        self.F1 = F1
        self.F2 = F2
        self.P = P0
        self.T = T0
        self.nC = nC
        self.nH = nH
        self.FAR = FAR
        self.Fluid = FluidBGM(self.nC, self.nH, self.FAR, self.T)
        self.delta_Qm = 0
        self.deltaT = 0
        self.E1 = EffortTF(self.P, self.T, self.Fluid.h, self.Fluid.u, self.Fluid.cp, self.Fluid.gamma, self.Fluid.R,
                           self.FAR)
        self.E2= self.E1

    def Param(self, Volume):
        self.Volume = Volume
        self.m = self.P / self.Fluid.R / self.T * self.Volume

    def Solve(self, dt, method='Euler'):
        self.Fluid = FluidBGM(self.nC, self.nH, self.FAR, self.T)

        "mass balance"
        self.delta_Qm_prev = self.delta_Qm
        self.delta_Qm = self.F1.Qm + self.F2.Qm
        self.m = Integrator(self.m, self.delta_Qm, dt, self.delta_Qm_prev, method)

        "energy balance"
        delta_Qh = self.F1.Qmh + self.F2.Qmh
        self.deltaT_prev = self.deltaT
        self.deltaT = (delta_Qh - self.Fluid.u * self.delta_Qm) / self.m / (self.Fluid.cp - self.Fluid.R)
        self.T = Integrator(self.T, self.deltaT, dt, self.deltaT_prev, method)
        self.P = self.m * self.Fluid.R * self.T / self.Volume

        "effort port creation"
        self.E1 = EffortTF(self.P, self.T, self.Fluid.h, self.Fluid.u, self.Fluid.cp, self.Fluid.gamma, self.Fluid.R,
                           self.FAR)
        self.E2 = self.E1


"------------------------------------------------------------------------"
"Compressor function (Tf element)"
"------------------------------------------------------------------------"


class Compressor_Tf:
    def __init__(self, E1, E2, Fm, nC=10.8, nH=18.7, FAR=0):
        self.E1 = E1
        self.E2 = E2
        self.Fm = Fm
        self.nC = nC
        self.nH = nH
        self.FAR = FAR
        self.Qm = 0
        self.Qmh = self.Qm * self.E1.h
        self.Tq=0
        self.F1 = FlowTF(-self.Qm, -self.Qmh)
        self.F2 = FlowTF(self.Qm, self.Qmh)
        self.Em = EffortM(self.Tq)

    def Param(self, Prefc, Trefc, x_NC, surge_PR, y_margin, z_flow_cor, z_eta_Comp, ):
        self.Prefc = Prefc
        self.Trefc = Trefc
        self.x_NC = x_NC
        self.surge_PR = surge_PR
        self.y_margin = y_margin
        self.z_flow_cor = z_flow_cor
        self.z_eta_Comp = z_eta_Comp

    def Solve(self):
        "massic flow calculation"
        NC_cor = self.Fm.N / (self.E1.T / self.Trefc) ** 0.5
        PRC = self.E2.P / self.E1.P
        PRC_ref = 0
        PRC_surge = interpolv(self.x_NC, self.surge_PR, NC_cor)
        surge = min((PRC - PRC_ref) / (PRC_surge - PRC_ref), 1.1)
        Qm_cor = max(1e-10, interpolm(self.y_margin, self.x_NC, self.z_flow_cor, surge, NC_cor))
        self.Qm = Qm_cor * (self.E1.P / self.Prefc) / (self.E1.T / self.Trefc) ** 0.5

        "Outlet temperature calculation"
        T2_is = abs(self.E2.P / self.E1.P) ** ((self.E1.gamma - 1) / self.E1.gamma) * self.E1.T
        self.Fluid = FluidBGM(self.nC, self.nH, self.FAR, T2_is)
        min_eta = 0.4
        etaC_is = max(min_eta, interpolm(self.y_margin, self.x_NC, self.z_eta_Comp, surge, NC_cor))
        self.h2 = (self.Fluid.h - self.E1.h) / etaC_is + self.E1.h

        "torque calculation"
        self.Tq = -self.Qm * (self.h2 - self.E1.h) / (self.Fm.omega)

        "flow port creation"
        self.F1 = FlowTF(-self.Qm, -self.Qm*self.E1.h)
        self.F2 = FlowTF(self.Qm, self.Qm*self.h2)
        self.Em = EffortM(self.Tq)



"------------------------------------------------------------------------"
"Turbine function (Tf element)"
"------------------------------------------------------------------------"

class Turbine_TF:
    def __init__(self, E1, E2, Fm, VNT, nC=10.8, nH=18.7, FAR=0):
        self.E1 = E1
        self.E2 = E2
        self.Fm = Fm
        self.VNT=VNT
        self.nC = nC
        self.nH = nH
        self.FAR = FAR
        self.Qm = 0
        self.Qmh = self.Qm * self.E1.h
        self.Tq=0
        self.F1 = FlowTF(-self.Qm, -self.Qmh)
        self.F2 = FlowTF(self.Qm, self.Qmh)
        self.Em = EffortM(self.Tq)

    def Param(self,Preft, Treft, x_PR, y_VNTposition, z_flowT_cor, z_eta_Turb,):
        self.Preft = Preft
        self.Treft = Treft
        self.x_PR = x_PR
        self.y_VNTposition = y_VNTposition
        self.z_flowT_cor = z_flowT_cor
        self.z_eta_Turb = z_eta_Turb

    def Solve(self):
        "massic flow calculation"
        PRT = self.E1.P / self.E2.P
        Qm_cor = max(0, interpolm(self.x_PR, self.y_VNTposition, self.z_flowT_cor, PRT, self.VNT))
        self.Qm = Qm_cor * (self.E1.P / self.Preft) / (self.E1.T / self.Treft) ** 0.5

        "Outlet temperature calculation"
        T2_is = abs(self.E2.P / self.E1.P) ** ((self.E1.gamma - 1) / self.E1.gamma) * self.E1.T
        self.Fluid = FluidBGM(self.nC, self.nH, self.FAR, T2_is)
        min_eta = 0.1
        etaT_is = max(min_eta, interpolm(self.x_PR, self.y_VNTposition, self.z_eta_Turb, PRT, self.VNT))
        self.h2 = (self.Fluid.h - self.E1.h) * etaT_is + self.E1.h

        "torque calculation"
        self.Tq = self.Qm * (self.E1.h - self.h2) / (self.Fm.omega)

        "flow port creation"
        self.F1 = FlowTF(-self.Qm, -self.Qm*self.E1.h)
        self.F2 = FlowTF(self.Qm, self.Qm*self.h2)
        self.Em = EffortM(self.Tq)


"------------------------------------------------------------------------"
"Engine function (Tf element)"
"------------------------------------------------------------------------"

class Engine_Tf:
    def __init__(self, E1, E2, Fm, Ffuel, Fuel, Prefm=1e5, Trefm=298, FAR=0):
        self.E1 = E1
        self.E2 = E2
        self.Fm = Fm
        self.Ffuel = Ffuel
        self.Fuel = Fuel
        self.Prefm = Prefm
        self.Trefm = Trefm
        self.FAR = FAR
        self.Qm = 0
        self.Qmh = self.Qm * self.E1.h
        self.Tq=0
        self.F1 = FlowTF(-self.Qm, -self.Qmh)
        self.F2 = FlowTF(self.Qm, self.Qmh)
        self.Em = EffortM(self.Tq)
        self.Efuel = self.E2

    def Param(self, Vcyl, x_NE, y_rho1rho2, y_etavol_overall, z_etavol, z_etaind, z_etacomb, Pwf = 0):
        self.Pwf = Pwf
        self.Vcyl = Vcyl
        self.x_NE = x_NE
        self.y_rho1rho2 = y_rho1rho2
        self.y_etavol_overall = y_etavol_overall
        self.z_etavol = z_etavol
        self.z_etaind = z_etaind
        self.z_etacomb = z_etacomb

    def Solve(self):
        "Efficiencies calculation"
        Eta_vol = interpolm(self.y_rho1rho2, self.x_NE, self.z_etavol, 1, self.Fm.N)
        Eta_ind = interpolm(self.y_etavol_overall, self.x_NE, self.z_etaind, Eta_vol * self.E1.P * self.Trefm / self.Prefm / self.E1.T, self.Fm.N)
        Eta_dT = interpolm(self.y_etavol_overall, self.x_NE, self.z_etacomb, Eta_vol * self.E1.P * self.Trefm / self.Prefm / self.E1.T, self.Fm.N)

        "inlet massic flow calculation"
        Qv_theor = self.Fm.N * self.Vcyl / 120
        self.Qm = Qv_theor * self.E1.P / self.E1.T / self.E1.R * Eta_vol

        "fuel injected massic flow calculation"
        if self.Ffuel.Qm > (self.Qm / self.Fuel.Ks):
            Qinj_eff = self.Qm / self.Fuel.Ks
        else:
            Qinj_eff = self.Ffuel.Qm
        Pwfuel_eff = Qinj_eff * self.Fuel.LHV
        self.FAR = self.Ffuel.Qm * self.Fuel.Ks / self.Qm

        "outlet massic flow calculation"
        Qm2 = self.Qm + self.Ffuel.Qm

        "engine pumping calculation"
        Pwi_bp = (self.E2.P - self.E1.P) * Qv_theor

        "Frictions calculation"
        "self.Pwf = 0"

        "indicated power calculation"
        Pwi_hp = Eta_ind * Pwfuel_eff

        "delivered power calculation"
        Pwe = Pwi_hp - self.Pwf - Pwi_bp

        "Outlet temperature calculation"
        Pwech = Eta_dT * Pwfuel_eff
        h2 = (Pwech + self.Qm * self.E1.h - self.Ffuel.Qm * self.Fuel.Hv) / Qm2

        "torque calculation"
        self.Tq = Pwe / (self.Fm.omega)

        "flow port creation"
        self.F1 = FlowTF(-self.Qm, -self.Qm*self.E1.h)
        self.F2 = FlowTF(Qm2, Qm2*h2)
        self.Em = EffortM(self.Tq)


