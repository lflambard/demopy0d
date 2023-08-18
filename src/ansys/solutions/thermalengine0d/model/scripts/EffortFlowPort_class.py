#Effort & Flow ports definition
import math
"-----------------------------------------------------------"
"THERMO FLUID"
"-----------------------------------------------------------"
class EffortTF:
    def __init__(self, P, T, h, u, Cp, gamma, R, FAR):
        self.P = P
        self.T = T
        self.h = h
        self.u = u
        self.Cp = Cp
        self.gamma = gamma
        self.R = R
        self.FAR = FAR

class FlowTF:
    def __init__(self, Qm, Qmh, Phi=0):
        self.Qm = Qm
        self.Qmh = Qmh
        self.Phi = Phi

"-----------------------------------------------------------"
"MECHANICS ROTATION"
"-----------------------------------------------------------"
class EffortM:
    def __init__(self, Tq):
        self.Tq = Tq

class FlowM:
    def __init__(self, omega):
        self.omega = omega
        self.N = omega * 30 / math.pi


"-----------------------------------------------------------"
"MECHANICS TRANSLATION"
"-----------------------------------------------------------"
class EffortMT:
    def __init__(self, Fx, Fy=0, Fz=0, Mx=0, My=0, Mz=0):
        self.Fx = Fx
        self.Fy = Fy
        self.Fz = Fz
        self.Mx = Mx
        self.My = My
        self.Mz = Mz


class FlowMT:
    def __init__(self, u, v=0, w=0, p=0, q=0, r=0):
        self.u = u
        self.v = v
        self.w = w
        self.p = p
        self.q = q
        self.r = r


"-----------------------------------------------------------"
"ELECTRICS"
"-----------------------------------------------------------"
class EffortE:
    def __init__(self, U):
        self.U = U

class FlowE:
    def __init__(self, I, Capacity=0, Pwconsumed=0):
        self.I = I
        self.Capacity = Capacity
        self.Pwconsumed = Pwconsumed

"-----------------------------------------------------------"
"FLUIDS"
"-----------------------------------------------------------"

class FlowF:
    def __init__(self, Qm, Qmh, Phi=0):
        self.Qm = Qm
        self.Qmh = Qmh
        self.Phi = Phi