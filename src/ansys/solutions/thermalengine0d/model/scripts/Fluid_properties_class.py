#Fluid properties for combustion gas and Fuel
import math


class FluidBGM:

    def __init__(self,nC, nH, FAR, T, P=0, Tcomb=0, CO=0):
        rich = FAR
        "Epsilon calculation (cf Heywood p103)"
        epsilon = 4 / (4 + nH / nC)

        "number total of moles calculation (rich = F/A ratio)"
        if rich <= 1:
            nTOT = (1 - epsilon) * rich + 1 + 3.773
        else:
            nTOT = (2 - epsilon) * rich + 3.773

        nCO = CO * nTOT

        if nCO <= 0 and Tcomb > 0:
            "calcul de la constante d'équilibre de la réaction CO2+H2=CO+H2O fonction de la température"
            "cf Heywood p104"
            k = math.exp(2.743 - 1761 / Tcomb - 1611000 / Tcomb ** 2 + 280300000 / Tcomb ** 3)

            if rich > 1:
                "calcul du nombre de moles de CO(cf Heywood p104)"
                "équation du second ordre : x=(-b+-sqrt(b^2-4ac))/2a"
                a = k - 1
                b = -k * (2 * (rich - 1) + epsilon * rich) - 2 * (1 - epsilon * rich)
                c = 2 * k * epsilon * rich * (rich - 1)
                nCO = (-b - (b ** 2 - 4 * a * c)**2) / 2 * a

        if rich > 1:
            nCO2 = epsilon * rich - nCO
            nH2O = 2 * (1 - epsilon * rich) + nCO
            nH2 = 2 * (rich - 1) - nCO
            nO2 = 0
            nN2 = 3.773
        else:
            "détermination des nombres de moles des autres composants"
            nCO2 = epsilon * rich
            nH2O = 2 * (1 - epsilon) * rich
            nH2 = 0
            nO2 = 1 - rich
            nN2 = 3.773
            nCO = 0

        "y1 pourcentage molaire de CO2"
        "y2 pourcentage molaire de H2O"
        "y3 pourcentage molaire de CO"
        "y4 pourcentage molaire de H2"
        "y5 pourcentage molaire de O2"
        "y6 pourcentage molaire de N2"

        y1 = nCO2 / nTOT
        y2 = nH2O / nTOT
        y3 = nCO / nTOT
        y4 = nH2 / nTOT
        y5 = nO2 / nTOT
        y6 = nN2 / nTOT

        y = [y1, y2, y3, y4, y5, y6]

        r = 8.3143
        mC = 0.012011 # Masse molaire de C (kg/mole)
        mO = 0.016   # Masse molaire de O (kg/mole)
        mH = 0.001008 # Masse molaire de H (kg/mole)
        mN = 0.01408 # Masse molaire de N (kg/mole)
        P0 = 100000  # Pression de référence 1 bar
        Tref = 298.15   # Température de référence (K)


        if P <= 0:
            P = P0

        "Coefficients des propriétés thermodynamiques"
        " h/R=ai1T + ai2T^2/2 + ai3T^3/3 + ai4T^4/4 + ai5T^5/5 +ai6"
        " s/R=ai1lnT + ai2T + ai3T^2/2 + ai4T^3/3 +ai5T4/4 +ai7"
        " page 131 du Heywood"
        ai_CO2_1 = [2.4008, 0.0087351, -0.0000066071, 0.0000000020022, 6.3274E-16, -48378, 9.6951]
        ai_CO2_2 = [4.4608, 0.0030982, -0.0000012393, 0.00000000022741, -1.5526E-14, -48961, -0.98636]

        ai_H2O_1 = [4.0701, -0.0011084, 0.0000041521, -0.0000000029637, 8.0702E-13, -30280, -0.3227]
        ai_H2O_2 = [2.7168, 0.0029451, -0.00000080224, 0.00000000010227, -4.8472E-15, -29906, 6.6306]

        ai_CO_1 = [3.7101, -0.0016191, 0.0000036924, -0.000000002032, 2.3953E-13, -14356, 2.9555]
        ai_CO_2 = [2.9841, 0.0014891, -0.000000579, 0.00000000010365, -6.9354E-15, -14245, 6.3479]

        ai_H2_1 =  [3.0574, 0.0026765, -0.0000058099, 0.000000005521, -1.8123E-12, -988.9, -2.2997]
        ai_H2_2 = [3.1002, 0.00051119, 0.000000052644, -0.00000000003491, 3.6945E-15, -877.38, -1.9629]

        ai_O2_1 = [3.6256, -0.0018782, 0.0000070555, -0.0000000067635, 2.1556E-12, -1047.5, 4.3053]
        ai_O2_2 = [3.622, 0.00073618, -0.00000019652, 0.000000000036202, -2.8946E-15, -1202, 3.6151]

        ai_N2_1 = [3.6748, -0.0012082, 0.000002324, -0.00000000063218, -2.2577E-13, -1061.2, 2.358]
        ai_N2_2 = [2.8963, 0.0015155, -0.00000057235, 0.000000000099807, -6.5224E-15, -905.86, 6.1615]

        m = [mC + 2 * mO, 2 * mH + mO, mC + mO, 2 * mH, 2 * mO, 2 * mN]


        " Masse molaire du mélange"
        M_mel=0
        for i in range(0,6):
            M_mel = M_mel + abs(y[i]) * m[i]



        if M_mel > 0:
            "Constante du gaz R_mel (J/kg/K)"
            R_mel = r / M_mel

            h_T = [T, T ** 2 / 2, T ** 3 / 3, T ** 4 / 4, T ** 5 / 5, 1, 0]
            h_Tref = [Tref, Tref ** 2 / 2, Tref ** 3 / 3, Tref ** 4 / 4, Tref ** 5 / 5, 1, 0]
            s_T = [math.log(T), T, T ** 2 / 2, T ** 3 / 3, T ** 4 / 4, 0, 1]
            cp_T = [1, T, T ** 2, T ** 3, T ** 4, 0, 0]

            h_CO2_r =0
            h_H2O_r = 0
            h_CO_r = 0
            h_H2_r = 0
            h_N2_r = 0
            h_O2_r = 0
            s_CO2_r = 0
            s_H2O_r = 0
            s_CO_r = 0
            s_H2_r = 0
            s_N2_r = 0
            s_O2_r = 0
            cp_CO2_r = 0
            cp_H2O_r = 0
            cp_CO_r = 0
            cp_H2_r = 0
            cp_N2_r = 0
            cp_O2_r =0

            if T < 1000:
                for i in range(0,6):
                    " Enthalpie réduite h/R "
                    h_CO2_r = h_CO2_r + ai_CO2_1[i] * h_T[i] - ai_CO2_1[i] * h_Tref[i]
                    h_H2O_r = h_H2O_r + ai_H2O_1[i] * h_T[i] - ai_H2O_1[i] * h_Tref[i]
                    h_CO_r = h_CO_r + ai_CO_1[i] * h_T[i] - ai_CO_1[i] * h_Tref[i]
                    h_H2_r = h_H2_r + ai_H2_1[i] * h_T[i] - ai_H2_1[i] * h_Tref[i]
                    h_N2_r = h_N2_r + ai_N2_1[i] * h_T[i] - ai_N2_1[i] * h_Tref[i]
                    h_O2_r = h_O2_r + ai_O2_1[i] * h_T[i] - ai_O2_1[i] * h_Tref[i]

                    " Entropie réduite s/R "
                    s_CO2_r = s_CO2_r + ai_CO2_1[i] * s_T[i]
                    s_H2O_r = s_H2O_r + ai_H2O_1[i] * s_T[i]
                    s_CO_r = s_CO_r + ai_CO_1[i] * s_T[i]
                    s_H2_r = s_H2_r + ai_H2_1[i] * s_T[i]
                    s_N2_r = s_N2_r + ai_N2_1[i] * s_T[i]
                    s_O2_r = s_O2_r + ai_O2_1[i] * s_T[i]

                    " Capacité calorifique réduite Cp/R "
                    cp_CO2_r = cp_CO2_r + ai_CO2_1[i] * cp_T[i]
                    cp_H2O_r = cp_H2O_r + ai_H2O_1[i] * cp_T[i]
                    cp_CO_r = cp_CO_r + ai_CO_1[i] * cp_T[i]
                    cp_H2_r = cp_H2_r + ai_H2_1[i] * cp_T[i]
                    cp_N2_r = cp_N2_r + ai_N2_1[i] * cp_T[i]
                    cp_O2_r = cp_O2_r + ai_O2_1[i] * cp_T[i]
            else:
                for i in range (0,6):
                    " Enthalpie réduite h/R "
                    h_CO2_r = h_CO2_r + ai_CO2_2[i] * h_T[i] - ai_CO2_2[i] * h_Tref[i]
                    h_H2O_r = h_H2O_r + ai_H2O_2[i] * h_T[i] - ai_H2O_2[i] * h_Tref[i]
                    h_CO_r = h_CO_r + ai_CO_2[i] * h_T[i] - ai_CO_2[i] * h_Tref[i]
                    h_H2_r = h_H2_r + ai_H2_2[i] * h_T[i] - ai_H2_2[i] * h_Tref[i]
                    h_N2_r = h_N2_r + ai_N2_2[i] * h_T[i] - ai_N2_2[i] * h_Tref[i]
                    h_O2_r = h_O2_r + ai_O2_2[i] * h_T[i] - ai_O2_2[i] * h_Tref[i]

                    " Entropie réduite s/R "
                    s_CO2_r = s_CO2_r + ai_CO2_2[i] * s_T[i]
                    s_H2O_r = s_H2O_r + ai_H2O_2[i] * s_T[i]
                    s_CO_r = s_CO_r + ai_CO_2[i] * s_T[i]
                    s_H2_r = s_H2_r + ai_H2_2[i] * s_T[i]
                    s_N2_r = s_N2_r + ai_N2_2[i] * s_T[i]
                    s_O2_r = s_O2_r + ai_O2_2[i] * s_T[i]

                    " Capacité calorifique réduite Cp/R"
                    cp_CO2_r = cp_CO2_r + ai_CO2_2[i] * cp_T[i]
                    cp_H2O_r = cp_H2O_r + ai_H2O_2[i] * cp_T[i]
                    cp_CO_r = cp_CO_r + ai_CO_2[i] * cp_T[i]
                    cp_H2_r = cp_H2_r + ai_H2_2[i] * cp_T[i]
                    cp_N2_r = cp_N2_r + ai_N2_2[i] * cp_T[i]
                    cp_O2_r = cp_O2_r + ai_O2_2[i] * cp_T[i]

            h_mel_r = h_CO2_r * y1 + h_H2O_r * y2 + h_CO_r * y3 + h_H2_r * y4 + h_O2_r * y5 + h_N2_r * y6
            s_mel_r = s_CO2_r * y1 + s_H2O_r * y2 + s_CO_r * y3 + s_H2_r * y4 + s_O2_r * y5 + s_N2_r * y6
            cp_mel_r = cp_CO2_r * y1 + cp_H2O_r * y2 + cp_CO_r * y3 + cp_H2_r * y4 + cp_O2_r * y5 + cp_N2_r * y6

            "Capacité calorifique Cp (J/kg/K)"
            cp_mel = cp_mel_r * R_mel
            "Enthalpie spécifique (J/kg)"
            h_mel = h_mel_r * R_mel
            u_mel = h_mel - R_mel * T
            "Masse volumique (kg/m3)"
            rho_mel = P / (R_mel * T)
            "Entropie spécifique (J/kg/K)"
            s_mel = s_mel_r * R_mel - R_mel * math.log(P / P0)
            "Calcul du gamma"
            gamma_mel = cp_mel / (cp_mel - R_mel)

        else:
            "Capacité calorifique Cp (J/kg/K)"
            cp_mel = 0
            "Enthalpie spécifique (J/kg)"
            h_mel = 0
            u_mel = 0
            "Masse volumique (kg/m3)"
            rho_mel = 0
            "Entropie spécifique (J/kg/K)"
            s_mel = 0
            "calcul du gamma"
            gamma_mel = 0
            R_mel = 0

        self.h=h_mel
        self.u=u_mel
        self.s=s_mel
        self.cp=cp_mel
        self.gamma=gamma_mel
        self.rho=rho_mel
        self.R=R_mel
        self.M=M_mel


class FluidFuel:
    def __init__(self, Ks, LHV, Hv, nC=10.8, nH=18.7):
        self.Ks = Ks
        self.LHV = LHV
        self.Hv = Hv
        self.nC = nC
        self.nH = nH

