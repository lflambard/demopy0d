# Fluid library
# Contains:
#   - Injector (Sf)


from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import FlowF
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolm


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
