#Electrical library
# Contains:
#   - Secundary LI Battery element (C)
import math

from ansys.solutions.thermalengine0d.model.scripts.Solver import Integrator_Euler
from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import EffortE, FlowE, EffortM
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolm, interpolv

"------------------------------------------------------------------------"
"Secundary LI Battery function (C element)"
"------------------------------------------------------------------------"

class LIBattery_C:
    def __init__(self, Fe):
        self.Fe = Fe
        self.U = 0
        self.Ee = EffortE(self.U)

    def Param(self, x_Capa, y_I, z_U, Nelement, Umin):
        self.x_Capa = x_Capa
        self.y_I = y_I
        self.z_U = z_U
        self.Nelement = Nelement
        self.Umin = Umin
        self.U = interpolm(self.x_Capa, self.y_I, self.z_U, self.Fe.Capacity / 3600, self.Fe.I) * self.Nelement
        self.Ee = EffortE(self.U)

    def Solve(self, dt, PowerOn=1):
        if PowerOn == 1:
            if self.U > self.Umin * self.Nelement:
                self.Fe.Capacity = Integrator_Euler(self.Fe.Capacity, self.Fe.I, dt)
                self.Fe.Pwconsumed = Integrator_Euler(self.Fe.Pwconsumed, self.U*self.Fe.I, dt)
                self.PowerOn = PowerOn
            else:
                self.Fe.I = 0
                self.PowerOn = 0

            self.U = interpolm(self.x_Capa, self.y_I, self.z_U, self.Fe.Capacity / 3600, self.Fe.I) * self.Nelement
            self.Ee = EffortE(self.U)


"------------------------------------------------------------------------"
"Electric motor function (Tf element)"
"------------------------------------------------------------------------"
class EMotor_Tf:
    def __init__(self, Ee, Fm, I_ord, alpha_mot):
        self.Ee = Ee
        self.Fm = Fm
        self.I_ord = I_ord
        self.alpha_mot = alpha_mot
        self.I = 0
        self.Tq = 0
        self.Fe = FlowE(self.I)
        self.Em = EffortM(self.Tq)

    def Param(self, x_Mot_Efficiency, y_Mot_Efficiency, x_alpha, y_U_alpha, z_alpha_cor):
        self.x_Mot_Efficiency = x_Mot_Efficiency
        self.y_Mot_Efficiency = y_Mot_Efficiency
        self.x_alpha = x_alpha
        self.y_U_alpha = y_U_alpha
        self.z_alpha_cor = z_alpha_cor


    def Solve(self, PowerOn=1):
        'Etamot=f(Nmot)'
        Etamot = 0.01 * interpolv(self.x_Mot_Efficiency, self.y_Mot_Efficiency, self.Fm.omega*30/math.pi)
        Imax = 1200
        self.I = min(interpolv([0, 30, 65, 195, 290], [0, 0, 62, 300, 515], self.I_ord) * interpolm(self.x_alpha, self.y_U_alpha,
                                                                                                self.z_alpha_cor, self.alpha_mot,
                                                                                                self.Ee.U), Imax)
        'Pwmot (W)'
        if PowerOn == 1:
            self.Pwmot = self.Ee.U * self.I
        else:
            self.Pwmot = 0

        'Tq motor out (Nm) = Tq Shaft in'
        self.Tq = self.Pwmot * Etamot / max(0.1, self.Fm.omega)

        self.Fe = FlowE(self.I)
        self.Em = EffortM(self.Tq)