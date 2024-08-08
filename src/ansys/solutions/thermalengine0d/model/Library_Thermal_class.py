# Thermo Fluid library
# Contains:
#   - Heat Transfer - HET (R)
#   - Source of Effort (Se)
#   - Source of Flow (Sf)

from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import EffortTH, FlowTH

"------------------------------------------------------------------------"
"Source of Effort (Se element)"
"------------------------------------------------------------------------"
class EffortSourceTH:
    def __init__(self, T=293):
        self.T = T
        self.Eth = EffortTH(self.T)

    def Param(self, T):
        self.T = T
        self.Eth = EffortTH(self.T)

    def Solve(self, dt, method='Euler'):
        self.dt = dt
        self.method = method

"------------------------------------------------------------------------"
"Source of Flow (Sf element)"
"------------------------------------------------------------------------"
class FlowSourceTH:
    def __init__(self, Phi=0):
        self.Phi = Phi
        self.Fth = FlowTH(self.Phi)

    def Param(self, Phi):
        self.Phi = Phi
        self.Fth = FlowTH(self.Phi)

    def Solve(self, dt, method='Euler'):
        self.dt = dt
        self.method = method
        self.Fth = FlowTH(self.Fth.Phi)



"------------------------------------------------------------------------"
"Heat Transfer (R element)"
"------------------------------------------------------------------------"
class HET_R:
    def __init__(self, Eth1=0, Eth2=0, Phi=0):
        if Eth1 == 0:
            self.Eth1 = EffortTH(293)
        else:
            self.Eth1 = Eth1

        if Eth2 == 0:
            self.Eth2 = EffortTH(293)
        else:
            self.Eth2 = Eth2

        self.Phi = Phi
        self.Fth1 = FlowTH(-self.Phi)
        self.Fth2 = FlowTH(self.Phi)

    def Param(self, h_conv, surf):
        self.h_conv = h_conv
        self.surf = surf

    def Solve(self, dt, method='Euler'):
        self.dt = dt
        self.method = method
        self.Phi = self.h_conv * self.surf * (self.Eth1.T - self.Eth2.T)

        "flow port creation"
        self.Fth1 = FlowTH(-self.Phi)
        self.Fth2 = FlowTH(self.Phi)

