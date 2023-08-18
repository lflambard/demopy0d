#Mechanical library
# Contains:
#   - Shaft element (I)
#   - Propeller element (Tf)
#   - Hydrodynamic 1D0F element (I)
#   - Hydrodynamic 6D0F element (I)
import math
import numpy as np
from ansys.solutions.thermalengine0d.model.scripts.Solver import Integrator
from ansys.solutions.thermalengine0d.model.scripts.EffortFlowPort_class import EffortM, FlowM, EffortMT, FlowMT
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolv
"------------------------------------------------------------------------"
"Shaft function (I element)"
"------------------------------------------------------------------------"

class Shaft_I:
    def __init__(self, Em1, Em2, omega0):
        self.Em1 = Em1
        self.Em2 = Em2
        self.omega = omega0
        self.delta_Tq = 0
        self.Fm1 = FlowM(self.omega)
        self.Fm2 = self.Fm1
        
    def Param(self, Inertia, Nmin, Etashaft=1):
        self.Inertia = Inertia
        self.Nmin = Nmin
        self.Etashaft = Etashaft
        
    def Solve(self, dt, method='Euler'):
        self.delta_Tq_prev = self.delta_Tq
        self.delta_Tq = (self.Em1.Tq * self.Etashaft + self.Em2.Tq) / self.Inertia

        if self.Fm1.N < self.Nmin and self.delta_Tq < 0:
            self.delta_Tq = 0

        self.omega = Integrator(self.omega, self.delta_Tq, dt, self.delta_Tq_prev, method)

        "Flow ports creation"
        self.Fm1 = FlowM(self.omega)
        self.Fm2 = self.Fm1

"------------------------------------------------------------------------"
"Propeller function (Tf element)"
"------------------------------------------------------------------------"

class Propeller_Tf:

    def __init__(self, Fm, Fmt):
        self.Fm = Fm
        self.Fmt = Fmt
        self.Tq = 0
        self.F = 0
        self.MotorMoment = 0
        self.Em = EffortM(self.Tq)
        self.Emt = EffortMT(self.F, 0, 0, self.MotorMoment, 0, 0)

    def Param(self, Rho_water, Kgear, Kwake, Ksuccion, Diam_prop, front_rear_ratio, Eta_adaptation, Kt_x, Kt_y, Kq_x, Kq_y):
        self.Rho_water = Rho_water
        self.Kgear = Kgear
        self.Kwake = Kwake
        self.Ksuccion = Ksuccion
        self.Diam_prop = Diam_prop
        self.front_rear_ratio = front_rear_ratio
        self.Eta_adaptation = Eta_adaptation
        self.Kt_x = Kt_x
        self.Kt_y = Kt_y
        self.Kq_x = Kq_x
        self.Kq_y = Kq_y

    def Solve(self):
        Nshaft = self.Fm.omega * 30 / math.pi / self.Kgear
        wshaft = Nshaft / 60
        Jprop = (self.Fmt.u * (1 - self.Kwake)) / max(0.0001, (wshaft * 2 / (1 + 1 / self.front_rear_ratio) * self.Diam_prop))
        Kt = interpolv(self.Kt_x, self.Kt_y, Jprop)
        Kq = interpolv(self.Kq_x, self.Kq_y, Jprop)

        self.F = Kt * self.Diam_prop ** 4 * self.Rho_water * (wshaft * 2 / (1 + 1 / self.front_rear_ratio)) ** 2 * (1 - self.Ksuccion)
        self.MotorMoment = math.pi/30 * Kq * self.Diam_prop ** 5 * self.Rho_water * (wshaft * 2 / (1 + 1 / self.front_rear_ratio)) ** 2
        Etaprop = (1 - self.Ksuccion) / (1 - self.Kwake) * self.Eta_adaptation * max(0.001, Jprop * Kt / max(0.01, Kq * 2 * math.pi))
        self.Tq = - self.F * self.Fmt.u / Etaprop / max(0.1, self.Fm.omega)

        "Effort ports creation"
        self.Em = EffortM(self.Tq)
        self.Emt = EffortMT(self.F, 0, 0, self.MotorMoment, 0, 0)


"------------------------------------------------------------------------"
"Hydrodynamic 1D (I element)"
"------------------------------------------------------------------------"

class Hydro1D_I:
    def __init__(self, Emt):
        self.Emt = Emt
        self.V = 0
        self.Acc_X = 0
        self.X = 0
        self.Fmt = FlowMT(self.V)

    def Param(self, Mass, Diam, Length, Sm, Volume, Xg, Zg, fins_S, fins_e, fins_c, Cmbeta, Cmw, Czbeta, Czw, Nu_water, Rho_water):
        self.Mass = Mass
        self.Diam = Diam
        self.Length = Length
        self.Sm = Sm
        self.Volume = Volume
        self.Xg = Xg
        self.Zg = Zg
        self.Nu_water = Nu_water
        self.Rho_water = Rho_water
        self.fins_S = fins_S
        self.fins_e = fins_e
        self.fins_c = fins_c
        self.Cmbeta= Cmbeta
        self.Cmw = Cmw
        self.Czw = Czw
        self.Czbeta = Czbeta


    def Solve(self, dt, method='Euler'):
        "Cx Model"
        if self.V > 0:
            Reynolds = self.V * self.Length / self.Nu_water
        else:
            Reynolds = 0.000001
        k0 = 1.3 * self.Diam / self.Length
        Ks = self.Sm / (math.pi * self.Diam * self.Length)
        fins_r = self.fins_e / self.fins_c
        if fins_r > 0.3:
            ka = 2 * fins_r + 35 * fins_r
        else:
            ka = 1.9 * fins_r + 125 * (fins_r) ** 4
        Cx0 = (1 + k0) * 0.082 / (math.log10(Reynolds) - 1.7) ** 2 * 4 * self.Length / self.Diam * Ks
        Cxa = (1 + ka) * 0.082 / (math.log10(Reynolds) - 1.7) ** 2 * self.fins_S / (self.Diam * self.Diam * math.pi / 4)
        Cx = (Cx0 + Cxa + 0.002) * 1.03

        "Drag Force"
        F_Drag = 0.5 * self.Rho_water * (math.pi * self.Diam * self.Diam / 4) * Cx * self.V * self.V

        "Pitch calculation"
        Mu_veh = self.Mass / (self.Rho_water * self.Volume)
        kdelta = self.Volume / (math.pi * self.Diam * self.Diam / 4) / self.Length
        coeff1 = 9.81000042 * 2 * kdelta * Mu_veh
        coeff2 = (self.V ** 2 * (self.Cmbeta - self.Cmw * self.Czbeta / self.Czw) + coeff1 * self.Zg / self.Czw)
        if self.V > 5:
            Beta_eq = coeff1 * self.Xg / coeff2 + (Mu_veh - 1) * 9.81000042 * 2 * kdelta * self.Length * (
                    self.Cmw / self.Czw - 9.81000042 * 2 * kdelta * Mu_veh * self.Zg / self.V ** 2 / self.Czw) / coeff2
            Pitch_eq = (-self.Czbeta * Beta_eq / self.Czw - 9.81000042 * 2 * self.Length * kdelta * (Mu_veh - 1) / self.Czw / self.V ** 2) * 180 / math.pi
        else:
            Beta_eq = 0
            Pitch_eq = 0
        Kincidence = 1 + 0.025 * Pitch_eq ** 2
        self.Beta_eq = Beta_eq * 180 / math.pi
        self.Pitch_eq = Pitch_eq

        "Acceleration, speed and position calculation"
        self.Acc_X_prev = self.Acc_X
        self.V_prev = self.V
        self.Acc_X = (self.Emt.Fx - F_Drag * Kincidence) / self.Mass
        self.V = Integrator(self.V, self.Acc_X, dt, self.Acc_X_prev, method)
        self.X = Integrator(self.X, self.V, dt, self.V_prev, method)

        "Flow ports creation"
        self.Fmt = FlowMT(self.V)


"------------------------------------------------------------------------"
"Hydrodynamic 6D (I element)"
"------------------------------------------------------------------------"

class Hydro6D_I:
    def __init__(self, Emt, Rudders=None):
        if Rudders is None:
            Rudders = [0, 0, 0, 0]
        self.Emt = Emt
        self.Rudders = Rudders
        self.u = 0
        self.v = 0
        self.w = 0
        self.p = 0
        self.q = 0
        self.r = 0
        self.Acc_X = 0
        self.Acc_Y = 0
        self.Acc_Z = 0
        self.dtp = 0
        self.dtq = 0
        self.dtr = 0
        self.X = 0
        self.Y = 0
        self.Z = 0
        self.phi = 0
        self.theta = 0
        self.psi = 0
        self.Vx = 0
        self.Vy = 0
        self.Vz = 0
        self.dtPhi = 0
        self.dtTheta = 0
        self.dtPsi = 0
        self.Fmt = FlowMT(self.u, self.v, self.w, self.p, self.q, self.r)

    def Param(self, Mass, Diam, Length, Sm, Volume, Xg, Yg, Zg, fins_S, fins_e, fins_c, Nu_water, Rho_water):
        self.Mass = Mass
        self.Diam = Diam
        self.Length = Length
        self.Sm = Sm
        self.Volume = Volume
        self.Xg = Xg
        self.Yg = Yg
        self.Zg = Zg
        self.Nu_water = Nu_water
        self.Rho_water = Rho_water
        self.fins_S = fins_S
        self.fins_e = fins_e
        self.fins_c = fins_c
        self.F = math.pi * self.Diam ** 2 / 4
        self.V_norm = 21.6
        self.Ix = 0.00133 * self.Length ** 2 * self.Mass
        self.Iy = 0.06506983 * self.Length ** 2 * self.Mass
        self.Iz = 0.06506983 * self.Length ** 2 * self.Mass
        self.xa = 0
        self.ya = 0
        self.za = 0


    def Solve(self, dt, method='Euler'):
        self.Xu_p = -0 * self.Rho_water * self.Volume
        self.Yr = 1.07 * self.Length * self.Rho_water / 2 * self.F
        self.Yr_p = 0 * self.Length * self.Rho_water * self.Volume
        self.Yv = -2.59 * self.Rho_water / 2 * self.F
        self.Yv_p = -1.00012293 * self.Rho_water * self.Volume
        self.Yvr = 0
        self.Yvqq = 0
        self.Yzeta_Kro = -0.1859 * self.Rho_water / 2 * self.F
        self.Yzeta_Kru = -0.17745 * self.Rho_water / 2 * self.F
        self.Zq = -1.391 * self.Length * self.Rho_water / 2 * self.F
        self.Zq_p = 0 * self.Length * self.Rho_water * self.Volume
        self.Zw = -1.7353 * self.Rho_water / 2 * self.F
        self.Zw_p = -1.00012293 * self.Rho_water * self.Volume
        self.Zwq = 0
        self.Zwrr = 0
        self.Zeta_Trr = 0.171 * self.Rho_water / 2 * self.F
        self.Zeta_Trl = 0.171 * self.Rho_water / 2 * self.F
        self.Kv = 0.023 * self.Length * self.Rho_water / 2 * self.F
        self.Kr = 0.01 * self.Length ** 2 * self.Rho_water / 2 * self.F
        self.Kp = -0.002 * self.Length ** 2 * self.Rho_water / 2 * self.F
        self.Kp_p = -0 * self.Length ** 2 * self.Rho_water * self.Volume
        self.Kqsi_Kro = -0.003604 * self.Length * self.Rho_water / 2 * self.F
        self.Kqsi_Kru = 0.003604 * self.Length * self.Rho_water / 2 * self.F
        self.Kqsi_Trr = 0.003604 * self.Length * self.Rho_water / 2 * self.F
        self.Kqsi_Trl = -0.003604 * self.Length * self.Rho_water / 2 * self.F
        self.Mq = -0.624 * self.Length ** 2 * self.Rho_water / 2 * self.F
        self.Mq_p = -0.05848689 * self.Length ** 2 * self.Rho_water * self.Volume
        self.Mqq = 0
        self.Mqqq = 0
        self.Mw = 0.40736 * self.Length * self.Rho_water / 2 * self.F
        self.Mw_p = 0 * self.Length * self.Rho_water * self.Volume
        self.Mwrr = 0
        self.Mwq = 0
        self.Meta_Trr = 0.076 * self.Length * self.Rho_water / 2 * self.F
        self.Meta_Trl = 0.076 * self.Length * self.Rho_water / 2 * self.F
        self.Mr = 0
        self.Ne = 0
        self.Nr = -0.61 * self.Length ** 2 * self.Rho_water / 2 * self.F
        self.Nr_p = -0.05848689 * self.Length ** 2 * self.Rho_water * self.Volume
        self.Nrr = 0
        self.Nrrr = 0
        self.Nv = -0.608 * self.Length * self.Rho_water / 2 * self.F
        self.Nv_p = 0 * self.Length * self.Rho_water * self.Volume
        self.Nvr = 0
        self.Nvqq = 0
        self.Nzeta_Kro = 0.08382 * self.Length * self.Rho_water / 2 * self.F
        self.Nzeta_Kru = 0.08001 * self.Length * self.Rho_water / 2 * self.F
        self.CIND = 0

        Hydromatrix = np.array([[self.Mass - self.Xu_p, 0, 0, 0, self.Mass * self.Zg, - self.Mass * self.Yg],
                                [0, self.Mass - self.Yv_p, 0, - self.Mass * self.Zg, 0, self.Mass * self.Xg - self.Yr_p],
                                [0, 0, self.Mass - self.Zw_p, self.Mass * self.Yg, - self.Mass * self.Xg - self.Zq_p, 0],
                                [0, - self.Mass * self.Zg, self.Mass * self.Yg, self.Ix - self.Kp_p, 0, 0],
                                [self.Mass * self.Zg, 0, - self.Mass * self.Xg - self.Mw_p, 0, self.Iy - self.Mq_p, 0],
                                [-self.Mass * self.Yg, self.Mass * self.Xg - self.Nv_p, 0, 0, 0, self.Iz - self.Nr_p]])

        self.Hydromatrix = np.linalg.inv(Hydromatrix)

        g = 9.80665
        Rudder_efficiency_Xi = 1
        Rudder_efficiency_Eta = 1
        Rudder_efficiency_Zeta = 1
        G = self.Mass * g
        A = self.Rho_water * self.Volume * g
        GMA = G - A
        "Cx Model"
        if self.Fmt.u > 0:
            Reynolds = self.Fmt.u * self.Length / self.Nu_water
        else:
            Reynolds = 0.000001
        k0 = 1.3 * self.Diam / self.Length
        Ks = self.Sm / (math.pi * self.Diam * self.Length)
        fins_r = self.fins_e / self.fins_c
        if fins_r > 0.3:
            ka = 2 * fins_r + 35 * fins_r
        else:
            ka = 1.9 * fins_r + 125 * (fins_r) ** 4
        Cx0 = (1 + k0) * 0.082 / (math.log10(Reynolds) - 1.7) ** 2 * 4 * self.Length / self.Diam * Ks
        Cxa = (1 + ka) * 0.082 / (math.log10(Reynolds) - 1.7) ** 2 * self.fins_S / (self.Diam * self.Diam * math.pi / 4)
        Cx = (Cx0 + Cxa + 0.002) * 1.03
        self.V = math.sqrt(self.Fmt.u ** 2 + self.Fmt.v ** 2 + self.Fmt.w ** 2)
        "Drag Force"
        F_Drag = 0.5 * self.Rho_water * (math.pi * self.Diam * self.Diam / 4) * Cx * self.V * self.V

        "Acceleration, speed and position calculation"
        SumX = self.Emt.Fx - F_Drag + GMA * -math.sin(self.theta) - self.Mass * (
                    self.q * self.w - self.r * self.v - self.Xg * (self.q ** 2 + self.r ** 2)
                    + self.Yg * self.p * self.q + self.Zg * self.p * self.r)

        SumY = self.Yv * self.v * self.V + self.Yr * self.r * self.V + Rudder_efficiency_Zeta * (
                   self.Yzeta_Kru * self.Rudders[1] + self.Yzeta_Kro * self.Rudders[0]) * self.V ** 2 +\
               GMA * math.cos(self.theta) * math.sin(self.phi) - self.Mass * (self.r * self.u - self.p * self.w
                    - self.Yg * (self.p ** 2 + self.r ** 2) + self.Xg * self.p * self.q + self.Zg * self.q * self.r)

        SumZ = self.Zw * self.w * self.V + self.Zq * self.q * self.V + Rudder_efficiency_Eta * (
                self.Zeta_Trr * self.Rudders[3] + self.Zeta_Trl * self.Rudders[2]) * self.V ** 2 + \
               GMA * math.cos(self.theta) * math.cos(self.phi) - \
               self.Mass * (self.p * self.v - self.q * self.u + self.Yg * self.q * self.r - self.Zg * (self.p ** 2 + self.q ** 2) + self.Xg * self.r * self.p)

        SumK = self.Emt.Mx + self.Kv * self.v * self.V + self.Kr * self.r * self.V + self.Kp * self.p * self.V + \
               Rudder_efficiency_Xi * (self.Kqsi_Kro * self.Rudders[0] + self.Kqsi_Kru * self.Rudders[1]
                                       + self.Kqsi_Trr * self.Rudders[3] + self.Kqsi_Trl * self.Rudders[2]) * self.V ** 2 \
               - self.Mass * (self.Yg * (self.p * self.v - self.u * self.q) + self.Zg * (self.w * self.p - self.u * self.r)) +\
               (self.Iy - self.Iz) * self.q * self.r - self.Zg * G * math.cos(self.theta) * math.sin(self.phi) + \
               self.Yg * G * math.cos(self.theta) * math.cos(self.phi)

        SumM = self.Mw * self.w * self.V + self.Mq * self.q * self.V + \
               Rudder_efficiency_Eta * (self.Meta_Trr * self.Rudders[3] + self.Meta_Trl * self.Rudders[2]) * self.V ** 2 - \
               self.Xg * G * math.cos(self.theta) * math.cos(self.phi) - self.Zg * G * math.sin(self.theta) - \
               self.r * self.p * (self.Ix - self.Iz) - self.Mass * self.Zg * (self.w * self.q - self.r * self.v) + \
               self.Mass * self.Xg * (self.p * self.v - self.u * self.q)

        SumN = self.Nv * self.v * self.V + self.Nr * self.r * self.V + \
               Rudder_efficiency_Zeta * (self.Nzeta_Kro * self.Rudders[0] + self.Nzeta_Kru * self.Rudders[1]) * self.V ** 2 +\
               self.Xg * G * math.cos(self.theta) * math.sin(self.phi) - self.p * self.q * (self.Iy - self.Ix) - \
               self.Mass * self.Xg * (self.r * self.u - self.p * self.w) - self.Mass * self.Yg * (self.v * self.r - self.w * self.q) +\
               self.Yg * G * math.sin(self.theta)

        Forces = np.array([SumX, SumY, SumZ, SumK, SumM, SumN])
        self.dtstates = np.dot(self.Hydromatrix, Forces)

        Body = np.ones([3, 3])
        Body[0, 0] = math.cos(self.theta) * math.cos(self.psi)
        Body[0, 1] = math.cos(self.theta) * math.sin(self.psi)
        Body[0, 2] = -math.sin(self.theta)
        Body[1, 0] = -math.cos(self.phi) * math.sin(self.psi) + math.sin(self.phi) * math.sin(self.theta) * math.cos(self.psi)
        Body[1, 1] = math.cos(self.phi) * math.cos(self.psi) + math.sin(self.phi) * math.sin(self.theta) * math.sin(self.psi)
        Body[1, 2] = math.sin(self.phi) * math.cos(self.theta)
        Body[2, 0] = math.sin(self.phi) * math.sin(self.psi) + math.cos(self.phi) * math.sin(self.theta) * math.cos(self.psi)
        Body[2, 1] = -math.sin(self.phi) * math.cos(self.psi) + math.cos(self.phi) * math.sin(self.theta) * math.sin(self.psi)
        Body[2, 2] = math.cos(self.phi) * math.cos(self.theta)
        BodyT = np.transpose(Body)

        self.Vx_prev = self.Vx
        self.Vx = self.u * BodyT[0, 0] + self.v * BodyT[0, 1] + self.w * BodyT[0, 2]
        self.Vy_prev = self.Vy
        self.Vy = self.u * BodyT[1, 0] + self.v * BodyT[1, 1] + self.w * BodyT[1, 2]
        self.Vz_prev = self.Vz
        self.Vz = self.u * BodyT[2, 0] + self.v * BodyT[2, 1] + self.w * BodyT[2, 2]
        self.dtPhi_prev = self.dtPhi
        self.dtPhi = self.p + (self.q * math.sin(self.phi) + self.r * math.cos(self.phi)) * math.sin(self.theta) / math.cos(self.theta)
        self.dtTheta_prev = self.dtTheta
        self.dtTheta = self.q * math.cos(self.phi) - self.r * math.sin(self.phi)
        self.dtPsi_prev = self.dtPsi
        self.dtPsi = self.q * math.sin(self.phi) + self.r * math.cos(self.phi) / math.cos(self.theta)

        self.Acc_X_prev = self.Acc_X
        self.Acc_X = self.dtstates[0]
        self.Acc_Y_prev = self.Acc_Y
        self.Acc_Y = self.dtstates[1]
        self.Acc_Z_prev = self.Acc_Z
        self.Acc_Z = self.dtstates[2]
        self.dtp_prev = self.dtp
        self.dtp = self.dtstates[3]
        self.dtq_prev = self.dtq
        self.dtq = self.dtstates[4]
        self.dtr_prev = self.dtr
        self.dtr = self.dtstates[5]
        self.u = Integrator(self.u, self.Acc_X, dt, self.Acc_X_prev, method)
        self.v = Integrator(self.v, self.Acc_Y, dt, self.Acc_Y_prev, method)
        self.w = Integrator(self.w, self.Acc_Z, dt, self.Acc_Z_prev, method)
        self.p = Integrator(self.p, self.dtp, dt, self.dtp_prev, method)
        self.q = Integrator(self.q, self.dtq, dt, self.dtq_prev, method)
        self.r = Integrator(self.r, self.dtr, dt, self.dtr_prev, method)

        self.X = Integrator(self.X, self.Vx, dt, self.Vx_prev, method)
        self.Y = Integrator(self.Y, self.Vy, dt, self.Vy_prev, method)
        self.Z = Integrator(self.Z, self.Vz, dt, self.Vz_prev, method)
        self.phi = math.fmod(Integrator(self.phi, self.dtPhi, dt, self.dtPhi_prev, method) - math.pi, 2 * math.pi) \
                   - math.pi
        self.theta = Integrator(self.theta, self.dtTheta, dt, self.dtTheta_prev, method)
        self.psi = math.fmod(Integrator(self.psi, self.dtPsi, dt, self.dtPsi_prev, method), 2 * math.pi)


        "Flow ports creation"
        self.Fmt = FlowMT(self.u, self.v, self.w, self.p, self.q, self.r)









