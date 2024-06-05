# Functions used for a combustion model 1D
import math
import numpy as np

"-----------------------------------------------------------"
"Crank Angle (degree) calculation"
"-----------------------------------------------------------"
class CrankAngle:
    def __init__(self, omega):
        self.omega = omega
        self.CrankAngle = 0

    def Param(self, omega0, nCyl):
        self.omega0 = omega0
        self.nCyl = nCyl
        self.shift = np.arange(1, nCyl+1)
        self.CrankAngle = np.arange(1, self.nCyl + 1)
        for i in range(0, int(nCyl)):
            self.shift[i] = 4*180/nCyl*i

    def Solve(self, time):
        self.time = time
        self.N = self.omega * 30 / math.pi
        self.CrankAngle = np.remainder(self.time * self.N * 6 + self.omega0 + self.shift, 720)

"-----------------------------------------------------------"
"Simplified Cylinder pressure calculation"
"-----------------------------------------------------------"
class PcylSimple:
    def __init__(self, P1, P2, Pmi, CrankAngle, VolCyl):
        self.P1 = P1
        self.P2 = P2
        self.Pmi = Pmi
        self.CrankAngle = CrankAngle
        self.VolCyl = VolCyl
        self.Pcyl = P1

    def Param(self, Bore, Stroke, ConnectingRod, CompRatio, KcombCor):
        self.Bore = Bore / 1000
        self.Stroke = Stroke / 1000
        self.ConnectingRod = ConnectingRod / 1000
        self.CompRatio = CompRatio
        self.DeadVol = pow(self.Bore, 2) * math.pi / 4 * (self.Stroke / (self.CompRatio - 1))
        self.KcombCor = KcombCor
        self.GammaComb = 1.1
        self.GammaCompr = 1.31

    def Solve(self):
        Pcyl0 = self.P1 * pow(self.DeadVol * self.CompRatio, self.GammaCompr) / pow(self.VolCyl, self.GammaCompr)
        PistonStroke = (self.Stroke / 2 * (1 - math.cos(6.5799))) - (self.ConnectingRod * (math.sqrt(1 - pow(math.sin(6.5799) / (self.ConnectingRod * 2 / self.Stroke), 2)) - 1))
        VolCylComb = pow(self.Bore, 2) * (math.pi / 4) * (self.Stroke / (self.CompRatio - 1) + PistonStroke)
        if self.CrankAngle < 180:
            self.Pcyl = self.P1
        else:
            if self.CrankAngle < 360:
                self.Pcyl = Pcyl0
            else:
                if self.CrankAngle < 377:
                    self.Pcyl = Pcyl0 + self.KcombCor * (self.CrankAngle / 17 - 21.1765) * self.Pmi * pow(self.DeadVol, self.GammaComb) / pow(VolCylComb, self. GammaComb)
                else:
                    if self.CrankAngle < 540:
                        self.Pcyl = Pcyl0 + self.KcombCor * (self.Pmi * pow(self.DeadVol, self.GammaComb) / pow(self.VolCyl, self. GammaComb))
                    else:
                        self.Pcyl = self.P2


"--------------------------------------------------------------"
"Cylinder Mechanics (Piston / Connecting Rod / Crankshaft) - TF"
"--------------------------------------------------------------"
class Piston:
    def __init__(self, Pcyl, N, CrankAngle):
        self.Pcyl = Pcyl
        self.N = N
        self.CrankAngle = CrankAngle
        self.Vp = 0
        self.Tq = 0
        self.VolCyl = 0

    def Param(self, Bore, Stroke, ConnectingRod, Mass, CompRatio):
        self.Bore = Bore / 1000
        self.Stroke = Stroke / 1000
        self.ConnectingRod = ConnectingRod / 1000
        self.Mass = Mass
        self.CompRatio = CompRatio

    def GasPistonTransfer(self):
        "Gas-Piston tranfer"
        self.dVol_dt = self.Vp * pow(self.Bore, 2) * math.pi / 4
        self.Fp = self.Pcyl * pow(self.Bore, 2) * math.pi / 4

    def PistonDynamic(self):
        StrokeCoeff1 = math.cos(self.CrankAngle * math.pi / 180)
        StrokeCoeff2 = math.cos(self.CrankAngle * 2 * math.pi / 180) * self.ConnectingRod / math.sqrt(1 - pow(math.sin(self.CrankAngle * math.pi / 180) * self.ConnectingRod, 2))
        StrokeCoeff3 = math.cos(self.CrankAngle * math.pi / 180) * math.sin(self.CrankAngle * math.pi / 180) * math.sin(self.CrankAngle * 2 * math.pi / 180) * pow(self.ConnectingRod, 3) * 0.5 / pow(1 - pow(math.sin(self.CrankAngle * math.pi / 180) * self.ConnectingRod, 2), 1.5)
        self.FEng = self.Fp - self.Mass * pow(self.N * math.pi / 30, 2) * (self.Stroke / 2) * (StrokeCoeff1 + StrokeCoeff2 + StrokeCoeff3)


    def ConnectingRodCrankshaft(self):
        Dist = self.Stroke / 2 * math.sin(self.CrankAngle * math.pi / 180) + self.ConnectingRod / 2 * math.sin(self.CrankAngle * 2 * math.pi / 180) / math.sqrt(1 - pow(math.sin(self.CrankAngle * math.pi / 180) / (self.ConnectingRod * 2 / self.Stroke), 2)) / pow(self.ConnectingRod * 2 / self.Stroke, 2)
        self.VolCyl = pow(self.Bore, 2) * math.pi / 4 * (self.Stroke / (self.CompRatio - 1) + (1 - math.cos(self.CrankAngle * math.pi / 180)) * self.Stroke / 2 - self.ConnectingRod * (math.sqrt(1 - pow(math.sin(self.CrankAngle * math.pi /180) / (self.ConnectingRod * 2 / self.Stroke), 2)) - 1))
        self.Tq = self.FEng * Dist
        self.Vp = Dist * self.N * math.pi / 30

    def Solve(self):
        self.GasPistonTransfer()
        self.PistonDynamic()
        self.ConnectingRodCrankshaft()



