#Mechanical library
# Contains:
#   - Shaft element (I)

from ansys.solutions.thermalengine0d.solution.Solver import Integrator_Euler
from ansys.solutions.thermalengine0d.solution.EffortFlowPort_class import EffortM, FlowM

"------------------------------------------------------------------------"
"Shaft function (I element)"
"------------------------------------------------------------------------"

class Shaft_I:
    def __init__(self, Em1, Em2, omega0):
        self.Em1 = Em1
        self.Em2 = Em2
        self.omega = omega0
        self.Fm1 = FlowM(self.omega)
        self.Fm2 = self.Fm1
        
    def Param(self, Inertia, Nmin):
        self.Inertia = Inertia
        self.Nmin = Nmin
        
    def Solve(self, dt):
        delta_Tq = (self.Em1.Tq + self.Em2.Tq) / self.Inertia

        if self.Fm1.N < self.Nmin and delta_Tq < 0:
            delta_Tq = 0

        self.omega = Integrator_Euler(self.omega, delta_Tq, dt)

        "Flow ports creation"
        self.Fm1 = FlowM(self.omega)
        self.Fm2 = self.Fm1

