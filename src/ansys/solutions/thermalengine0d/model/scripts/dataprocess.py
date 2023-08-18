# Engine data pre processing from standard excel file
import xlrd
import numpy as np
from ansys.solutions.thermalengine0d.model.scripts.Fluid_properties_class import FluidBGM
import math
from configparser import ConfigParser


class PreProcess:

    def __init__(self, filename):
        self.filename = filename
        self.data = xlrd.open_workbook(self.filename)
        self.control = {}
        self.config = {}
        self.control['Engine_control'] = {}
        self.config['Integrators_init'] = {}
        self.config['Fuel_param'] = {}
        self.config['Engine_param'] = {}
        self.control['Engine_ECU'] = {}
        self.config['Compr_param'] = {}
        self.config['Turbine_param'] = {}
        self.config['AirFilter_param'] = {}
        self.config['Intercooler_param'] = {}
        self.config['Intake_param'] = {}
        self.config['Outlet_param'] = {}
        self.config['Exhaust_param'] = {}

    def control_data(self):
        data_control = self.data.sheet_by_name('ControlData')
        self.control['Engine_control']['p0'] = data_control.cell_value(0, 1) * 100
        self.control['Engine_control']['t0'] = data_control.cell_value(1, 1) + 273

        start_row = 5
        end_row = data_control.nrows

        self.control['Engine_control']['x_time_nord'] = data_control.col_values(0, start_row, end_row)
        self.control['Engine_control']['y_nord'] = data_control.col_values(1, start_row, end_row)
        self.control['Engine_control']['x_time_pps'] = data_control.col_values(0, start_row, end_row)
        self.control['Engine_control']['y_pps'] = data_control.col_values(2, start_row, end_row)

    def ecu_data(self):
        self.control['Engine_ECU']['kp'] = -1e-5
        self.control['Engine_ECU']['ki'] = 1
        self.control['Engine_ECU']['x_epsilon_kp'] = [-2E05, -1E05, -0.5E05, -0.1E05, 0, 0.1E05, 0.5E05, 1E05, 2E05]
        self.control['Engine_ECU']['y_kp'] = [-15E-05, -5E-05, -2.5E-05, -2.5E-05, -2.5E-05, -2.5E-05, -2.5E-05, -5E-05, -15E-05]
        self.control['Engine_ECU']['vnt_min'] = 0.1
        self.control['Engine_ECU']['vnt_max'] = 1

    def fuel_data(self):
        data_config = self.data.sheet_by_name('Fuel')
        self.config['Fuel_param']['ks'] = data_config.cell_value(7, 1)
        self.config['Fuel_param']['lhv'] = data_config.cell_value(5, 1) * 1e6
        self.config['Fuel_param']['hv'] = data_config.cell_value(6, 1)
        self.config['Fuel_param']['nc']: float = data_config.cell_value(1, 1)
        self.config['Fuel_param']['nh']: float = data_config.cell_value(2, 1)

    def integrator_data(self):
        self.config['Integrators_init']['p0']:float = 90000
        self.config['Integrators_init']['t0']:float = 300
        self.config['Integrators_init']['p2c'] = 100000
        self.config['Integrators_init']['t2c'] = 300
        self.config['Integrators_init']['p1e'] = 100000
        self.config['Integrators_init']['t1e'] = 300
        self.config['Integrators_init']['p2e'] = 100000
        self.config['Integrators_init']['p1t'] = 100000
        self.config['Integrators_init']['t1t'] = 700
        self.config['Integrators_init']['t2om'] = 700
        self.config['Integrators_init']['texhaust'] = 700
        self.config['Integrators_init']['vt'] = 0.02
        self.config['Integrators_init']['nturbo'] = 120000
        self.config['Integrators_init']['fa'] = 0


    def engine_data(self):
        data_config = self.data.sheet_by_name('Data Engine')
        self.config['Engine_param']['engine name'] = data_config.cell_value(0, 1)
        self.config['Engine_param']['vcyl'] = data_config.cell_value(3, 1)/1000
        self.config['Engine_param']['ncyl'] = data_config.cell_value(4, 1)
        self.config['AirFilter_param']['vol_af'] = data_config.cell_value(13, 1) * 1e-3
        self.config['Intercooler_param']['vol_ic'] = data_config.cell_value(14, 1) * 1e-3
        self.config['Intake_param']['vol_intake'] = data_config.cell_value(15, 1) * 1e-3
        self.config['Outlet_param']['vol_om'] = data_config.cell_value(16, 1) * 1e-3
        self.config['Exhaust_param']['vol_ex'] = data_config.cell_value(17, 1) * 1e-3
        self.config['Engine_param']['pair'] = data_config.cell_value(20, 1) * 1e2
        self.config['Engine_param']['tair'] = data_config.cell_value(21, 1) + 273


        "line reference of the file *.xls"
        "---------------------------------------"
        "1: engine speed(rpm), 2: engine power (kW), 3: fuel flow(kg/h), 4: air flow(g/s), "
        "5: smoke index(bosch), 6: turbo speed(rpm),"
        "7: T1C(°C), 8: T2C(°C), 9: T2I(°C), 10: T1E(°C), 11: T1T(°C), 12: T2T(°C), 13: T1x(°C),"
        "14: P0(hPa), 15: P1C(hPa), 16: P2C(hPa), 17: P1E(hPa), 18: P1T(hPa), 19: P2T(hPa),"
        deb_col: int = 2
        deb_row: int = 24
        self.MatriceEssai = np.zeros((data_config.nrows - deb_row, data_config.ncols - deb_col), dtype=float)
        self.config['Engine_param']['testdata'] = self.MatriceEssai
        rho_air = self.config['Engine_param']['pair'] / 287 / self.config['Engine_param']['tair']

        'variables notification'
        engine_speed = np.zeros(data_config.ncols - deb_col)
        Power = np.zeros(data_config.ncols - deb_col)
        fuel_flow = np.zeros(data_config.ncols - deb_col)
        air_flow = np.zeros(data_config.ncols - deb_col)
        Qinj_kg_stroke = np.zeros(data_config.ncols - deb_col)
        deltaP_AF = np.zeros(data_config.ncols - deb_col)
        Qv_AF = np.zeros(data_config.ncols - deb_col)
        deltaP_Intercooler = np.zeros(data_config.ncols - deb_col)
        Qv_intercooler = np.zeros(data_config.ncols - deb_col)
        deltaP_x = np.zeros(data_config.ncols - deb_col)
        Qv_exhaust = np.zeros(data_config.ncols - deb_col)
        Qvth = np.zeros(data_config.ncols - deb_col)
        Qmth = np.zeros(data_config.ncols - deb_col)
        Eta_vol = np.zeros(data_config.ncols - deb_col)
        Eta_vol_overall = np.zeros(data_config.ncols - deb_col)

        EtaComb = np.zeros(data_config.ncols - deb_col)
        CO = np.zeros(data_config.ncols - deb_col)
        Pwi_bp = np.zeros(data_config.ncols - deb_col)
        mep = np.zeros(data_config.ncols - deb_col)
        TqE = np.zeros(data_config.ncols - deb_col)
        Pwi_hp = np.zeros(data_config.ncols - deb_col)
        Qmfuel_eff = np.zeros(data_config.ncols - deb_col)
        Eta_ind = np.zeros(data_config.ncols - deb_col)
        Rho2Rho1 = np.zeros(data_config.ncols - deb_col)
        AF_lim= np.zeros(data_config.ncols - deb_col)
        PboostMin= np.zeros(data_config.ncols - deb_col)
        Pwmf = np.zeros(data_config.ncols - deb_col)
        Pwmf_access = np.zeros(data_config.ncols - deb_col)
        y_epsilon = np.zeros(data_config.ncols - deb_col)

        for i in range(0, (data_config.ncols - deb_col)):
            self.MatriceEssai[:, i] = data_config.col_values(i + deb_col, deb_row, data_config.nrows)
            engine_speed[i] = self.MatriceEssai[0, i]
            Power[i] = self.MatriceEssai[1, i]
            fuel_flow[i] = self.MatriceEssai[2, i]
            air_flow[i] = self.MatriceEssai[3, i]
            ' fuel flow (kg/stroke)'
            Qinj_kg_stroke[i] = 2 * fuel_flow[i] / (60 * engine_speed[i] * self.config['Engine_param']['ncyl'])
            'theoric volumetric flow (m3/s)'
            Qvth[i] = 0.5 * self.config['Engine_param']['vcyl'] * engine_speed[i] / 60
            'inlet engine density (kg/m3)and enthalpy (J/kg)'
            Fluid1E= FluidBGM(self.config['Fuel_param']['nc'], self.config['Fuel_param']['nh'], 0, self.MatriceEssai[9, i] + 273,(self.MatriceEssai[16, i] + self.MatriceEssai[13, i]) * 100)
            'theoric massic flow(kg/s)'
            Qmth[i]= Qvth[i] * Fluid1E.rho
            'volumetric efficiency'
            Eta_vol[i] = air_flow[i] / (Qmth[i] * 1000)
            'volumetric overall efficiency'
            Eta_vol_overall[i] = (Eta_vol[i] * (self.MatriceEssai[16, i] + self.MatriceEssai[13, i]) * 100 * (
                        self.MatriceEssai[6, i] + 273)) / ((self.MatriceEssai[9, i] + 273) * self.MatriceEssai[13, i] * 100)
            'pumping (W)'
            Pwi_bp[i] = Qvth[i] * (self.MatriceEssai[17, i] - self.MatriceEssai[16, i]) * 100
            'break mean effective pressure (Pa)'
            mep[i] = Power[i] * 1000 / (engine_speed[i] * self.config['Engine_param']['vcyl'] / 120)
            'Engine torque (Nm)'
            TqE[i] = Power[i] * 1000 / (engine_speed[i] * math.pi / 30)
            'High pressure power indicated (W)'
            Pwi_hp[i] = Power[i] * 1000 + Pwi_bp[i] + Pwmf[i] + Pwmf_access[i]
            'efficient fuel flow (kg/s)'
            Qmfuel_eff[i] = min(fuel_flow[i] / 3600, air_flow[i] / 1000 / self.config['Fuel_param']['ks'])
            'indicated efficiency'
            Eta_ind[i] = Pwi_hp[i] / (Qmfuel_eff[i] * self.config['Fuel_param']['lhv'])
            'rho1/rho2'
            FAR = self.config['Fuel_param']['ks'] * fuel_flow[i] / 3600 / (air_flow[i] / 1000)
            Fluid2E= FluidBGM(self.config['Fuel_param']['nc'], self.config['Fuel_param']['nh'], FAR, self.MatriceEssai[10, i] + 273, (self.MatriceEssai[17, i] + self.MatriceEssai[13, i]) * 100)
            Rho2Rho1[i] = Fluid2E.rho / Fluid1E.rho
            'combustion efficiency'
            EtaComb[i] = ((air_flow[i] / 1000 + fuel_flow[i] / 3600) * Fluid2E.h - air_flow[i] / 1000 * Fluid1E.h + self.config['Fuel_param']['hv'] * fuel_flow[i] / 3600) / (Qmfuel_eff[i] * self.config['Fuel_param']['lhv'])
            'Corrected Volumetric flow and pressure losses in the inlet of each component'
            Fluid1AF = FluidBGM(self.config['Fuel_param']['nc'], self.config['Fuel_param']['nh'], 0, self.MatriceEssai[6, i] + 273, self.MatriceEssai[13, i] * 100)
            deltaP_AF[i] = -self.MatriceEssai[14, i] * 100 * (rho_air / Fluid1AF.rho)
            Qv_AF[i] = (air_flow[i] / 1000) / Fluid1AF.rho
            Fluid1I = FluidBGM(self.config['Fuel_param']['nc'], self.config['Fuel_param']['nh'], 0, self.MatriceEssai[7, i] + 273, (self.MatriceEssai[15, i] + self.MatriceEssai[13, i]) * 100)
            deltaP_Intercooler[i] = max(0, (
                        self.MatriceEssai[15, i] - self.MatriceEssai[16, i]) * 100) * (rho_air / Fluid1I.rho)
            Qv_intercooler[i] = (air_flow[i] / 1000) / Fluid1I.rho
            Fluid1X = FluidBGM(self.config['Fuel_param']['nc'], self.config['Fuel_param']['nh'], 0, self.MatriceEssai[11, i] + 273, (self.MatriceEssai[18, i] + self.MatriceEssai[13, i]) * 100)
            deltaP_x[i] = self.MatriceEssai[18, i] * 100 * (rho_air / Fluid1X.rho)
            Qv_exhaust[i] = ((air_flow[i] / 1000) + (fuel_flow[i] / 3600)) / Fluid1X.rho
            AF_lim[i] = (air_flow[i] / 1000) / (fuel_flow[i] / 3600)
            PboostMin[i] = 110000
            y_epsilon[i] = (self.MatriceEssai[9, i] - self.MatriceEssai[7, i]) / (self.MatriceEssai[6, i] - self.MatriceEssai[7, i])

        '---------------------------'
        'creation of normalized map '
        '---------------------------'
        self.config['Engine_param']['x_ne'] = list(engine_speed)
        self.config['Engine_param']['y_rho1rho2'] = [0,1]
        self.config['Engine_param']['y_etavol_overall'] = [0, 1, 2]
        self.config['Engine_param']['y_far'] = [0, 1]
        self.control['Engine_ECU']['y_pps_qinj'] = [0, 1]
        self.control['Engine_ECU']['x_ne'] = list(engine_speed)
        self.config['Engine_param']['z_etavol'] = np.zeros((2, data_config.ncols - deb_col))
        self.config['Engine_param']['z_etavol'][0, :] = Eta_vol
        self.config['Engine_param']['z_etavol'][1, :] = Eta_vol
        self.config['Engine_param']['z_etacomb'] = np.zeros((3, data_config.ncols - deb_col))
        self.config['Engine_param']['z_etacomb'][0, :] = EtaComb
        self.config['Engine_param']['z_etacomb'][1, :] = EtaComb
        self.config['Engine_param']['z_etacomb'][2, :] = EtaComb
        self.config['Engine_param']['z_co'] = np.zeros((2, data_config.ncols - deb_col))
        self.config['Engine_param']['z_co'][0, :] = CO
        self.config['Engine_param']['z_co'][1, :] = CO

        coeff_Pwe_pl = 10
        coeff_bsfc_pl = 1.7
        coeff_etaind_pl = 0.6
        self.config['Engine_param']['z_etaind'] = np.zeros((3, data_config.ncols - deb_col))
        self.config['Engine_param']['z_etaind'][0, :] = Eta_ind * coeff_etaind_pl
        self.config['Engine_param']['z_etaind'][1, :] = Eta_ind
        self.config['Engine_param']['z_etaind'][2, :] = Eta_ind

        coeff_Qinj_pl = coeff_bsfc_pl / coeff_Pwe_pl
        self.control['Engine_ECU']['z_qinj'] = np.zeros((2, data_config.ncols - deb_col))
        self.control['Engine_ECU']['z_qinj'][0, :] = Qinj_kg_stroke * coeff_Qinj_pl
        self.control['Engine_ECU']['z_qinj'][1, :] = fuel_flow / 3600

        self.control['Engine_ECU']['z_p1e_ord'] = np.zeros((2, data_config.ncols - deb_col))
        self.control['Engine_ECU']['z_p1e_ord'][0, :] = self.MatriceEssai[13, :]*100
        self.control['Engine_ECU']['z_p1e_ord'][1, :] = (self.MatriceEssai[16, :] + self.MatriceEssai[13, :]) * 100

        self.config['Engine_param']['y_pwmf'] = Pwmf
        self.config['Engine_param']['y_access_pwmf'] = Pwmf_access
        self.config['Engine_param']['y_epsilon'] = y_epsilon
        self.K_pl_AF = np.polyfit(Qv_AF, deltaP_AF, 2)
        self.K_pl_Intake = np.polyfit(Qv_intercooler, deltaP_Intercooler, 2)
        self.K_pl_Exhaust = np.polyfit(Qv_exhaust, deltaP_x, 2)
        self.config['AirFilter_param']['k_pl_af'] = (1/self.K_pl_AF[0]) ** 0.5
        self.config['Intake_param']['k_pl_intake'] = (1 / self.K_pl_Intake[0]) ** 0.5
        self.config['Exhaust_param']['k_pl_exhaust'] = (1 / self.K_pl_Exhaust[0]) ** 0.5

    def compressor_data(self):
        data_config = self.data.sheet_by_name('Data Compr')
        self.config['Compr_param']['compressor name'] = data_config.cell_value(0, 1)
        self.config['Compr_param']['prefc'] = data_config.cell_value(3, 1) * 100
        self.config['Compr_param']['trefc'] = data_config.cell_value(4, 1) + 273
        self.config['Compr_param']['inertia'] = data_config.cell_value(5, 1)
        self.config['Compr_param']['vol_compr'] = data_config.cell_value(7, 1)
        self.config['Compr_param']['radius'] = data_config.cell_value(8, 1) / 2

        'Parameters for compressor field extrapolation'
        nb_ligne_extrap = 10
        nbpoint = 7
        pente_dr_nul = 1.5
        pente_rp_nul = 0.7
        reg_min = 10
        iso1_rp1 = 1
        iso1_coef_dr = 10
        iso1_coef_rp = 0.008

        'reading initial compressor data'
        deb_col: int = 0
        deb_row: int = 13
        self.field_comp = np.zeros((data_config.nrows - deb_row, 4))
        self.field_comp[:, 0] = data_config.col_values(deb_col, deb_row, data_config.nrows)
        self.field_comp[:, 1] = data_config.col_values(deb_col + 1, deb_row, data_config.nrows)
        self.field_comp[:, 2] = data_config.col_values(deb_col + 2, deb_row, data_config.nrows)
        self.field_comp[:, 3] = data_config.col_values(deb_col + 3, deb_row, data_config.nrows)

        'pumping margin vector creation'
        incr_marge = 0.01
        max_marge = 1.1
        min_marge = 0
        self.y_margin = np.linspace(max_marge, min_marge, int((max_marge - min_marge)/incr_marge) + 1)

        'first line iso speed'
        Qm0 = np.array([0.00408, 0.01224, 0.02041, 0.0245, 0.02859, 0.03268, 0.03677])
        Tx0 = np.array([0.9985, 0.9881, 0.969, 0.9543, 0.9387, 0.9189, 0.8948])

        new_field_comp = np.zeros((data_config.nrows - deb_row - 1 + (nb_ligne_extrap + 1) * nbpoint, 4))
        for i in range(0,data_config.nrows - deb_row - 1 + (nb_ligne_extrap + 1) * nbpoint):
            if i < 7:
                new_field_comp[i, 0] = reg_min
                new_field_comp[i, 1] = Qm0[i]
                new_field_comp[i, 2] = Tx0[i]
                new_field_comp[i, 3] = 0

            if i >= 7 and i < (nb_ligne_extrap + 1) * nbpoint:
                m = int(i / nbpoint)
                pos_ligne = m / (nb_ligne_extrap + 1)
                new_field_comp[i, 0] = pos_ligne * (self.field_comp[0, 0] - reg_min) + reg_min
                new_field_comp[i, 1] = 0.00755 * (pos_ligne * self.field_comp[i - m * nbpoint, 1] + (1 - pos_ligne) * Qm0[i - m * nbpoint] / 0.00755)
                new_field_comp[i, 2] = self.field_comp[i - m * nbpoint, 2] * ((1 + 6.41E-14 * self.config['Compr_param']['radius'] ** 2 * new_field_comp[i, 0] ** 2) / (1 + 6.41E-14 * self.config['Compr_param']['radius'] ** 2 * self.field_comp[0, 0] ** 2))
                new_field_comp[i, 3] = pow((max(0, (new_field_comp[i, 2] - 1) / (self.field_comp[i - m * nbpoint, 2] - 1))), 0.5) * self.field_comp[i - m * nbpoint, 3]
            if i >= (nb_ligne_extrap + 1) * nbpoint:
                new_field_comp[i, 0] = self.field_comp[i - (nb_ligne_extrap + 1) * nbpoint, 0]
                new_field_comp[i, 1] = self.field_comp[i - (nb_ligne_extrap + 1) * nbpoint, 1] * 0.00755
                new_field_comp[i, 2] = self.field_comp[i - (nb_ligne_extrap + 1) * nbpoint, 2]
                new_field_comp[i, 3] = self.field_comp[i - (nb_ligne_extrap + 1) * nbpoint, 3]

        self.field_comp = new_field_comp

        i = 0
        k = 0
        self.x_NC = np.array([])
        self.surge_PR = np.array([])
        self.surge_flow_cor = np.array([])
        self.z_pr = np.zeros((self.y_margin.size, int(self.field_comp.size / 4)))
        self.z_flow_cor = np.zeros((self.y_margin.size, int(self.field_comp.size / 4)))
        self.z_eta_Comp = np.zeros((self.y_margin.size, int(self.field_comp.size / 4)))
        while i < self.field_comp.size / 4:
            'iso_speed vector'
            self.x_NC = np.resize(self.x_NC, k+1)
            self.x_NC[k] = self.field_comp[i, 0]

            j = i
            test = j
            while j < self.field_comp.size / 4 and self.field_comp[i, 0] == self.field_comp[test, 0]:
                j = j + 1
                test = min(j, self.field_comp.size / 4)

            z_pr_temp = np.zeros(j - i+1)
            z_flow_cor_temp = np.zeros(j - i+1)
            z_eta_Comp_temp = np.zeros(j - i+1)
            for w in range(j - 1, i-1, -1):
                if w > i:
                    pente = (self.field_comp[w - 1, 2] - self.field_comp[w, 2]) / (self.field_comp[w, 1] - self.field_comp[w - 1, 1])
                    if pente <= 0:
                        self.field_comp[w - 1, 2] = pente_dr_nul * (self.field_comp[w, 1] - self.field_comp[w - 1, 1]) + self.field_comp[w, 2]
                z_flow_cor_temp[w - i+1] = self.field_comp[w, 1]
                z_pr_temp[w - i+1] = self.field_comp[w, 2]
                z_eta_Comp_temp[w - i+1] = self.field_comp[w, 3]

            if self.field_comp[i, 1] == 0:
                max1 = i + 1
                debit1 = self.field_comp[max1, 1]
                pres1 = self.field_comp[max1, 2]
                eta1 = self.field_comp[max1, 3]
            else:
                max1 = i
                debit1 = self.field_comp[max1, 1]
                pres1 = self.field_comp[max1, 2]
                eta1 = self.field_comp[max1, 3]
                z_flow_cor_temp[0] = 0
                z_eta_Comp_temp[0] = 0
                pression_max = pres1 + debit1 * pente_dr_nul
                z_pr_temp[0] = pression_max

            self.surge_PR = np.resize(self.surge_PR, k + 1)
            self.surge_PR[k] = pres1
            self.surge_flow_cor = np.resize(self.surge_flow_cor, k + 1)
            self.surge_flow_cor[k] = debit1

            if self.field_comp[j - 1, 2] == 0:
                max2 = j - 2
                debit2 = self.field_comp[max2, 1]
                pres2 = self.field_comp[max2, 2]
                eta2 = self.field_comp[max2, 3]
            else:
                max2 = j - 1
                debit2 = self.field_comp[max2, 1]
                pres2 = self.field_comp[max2, 2]
                eta2 = self.field_comp[max2, 3]
                coeff_pente = pres2 * pente_rp_nul
                debit_max = debit2 + (pres2) / (100 * coeff_pente)
                x0 = self.field_comp[max2, 1]
                y0 = self.field_comp[max2, 2]
                pe0 = -100 * coeff_pente
                pe1 = (y0 - self.field_comp[max2 - 1, 2]) / (x0 - self.field_comp[max2 - 1, 1])
                x1 = x0
                y1 = y0
                alpha = -pe0 - pe1
                beta = 2 * (x1 * (pe0 + pe1) - y1)
                gamma = x1 * (2 * y1 - x1 * (pe0 + pe1))
                debit_max2 = (-beta + pow((beta ** 2 - 4 * alpha * gamma), 0.5)) / (2 * alpha)
                a = (pe1 - pe0) / (2 * (x1 - debit_max2))
                b = pe1 - 2 * a * x1
                c = y1 - (a * x1 ** 2 + b * x1)

                debit_002 = x0 + 0.25 * (debit_max2 - x0)
                pres_002 = a * debit_002 ** 2 + b * debit_002 + c
                rend_002 = (pres_002 - 0.98) * 0.5

                debit_003 = x0 + 0.5 * (debit_max2 - x0)
                pres_003 = a * debit_003 ** 2 + b * debit_003 + c
                rend_003 = (pres_003 - 0.98) * 0.4

                debit_004 = x0 + 0.75 * (debit_max2 - x0)
                pres_004 = a * debit_004 ** 2 + b * debit_004 + c
                rend_004 = (pres_004 - 0.98) * 0.3

                z_pr_temp = np.resize(z_pr_temp, j - i + 5)
                z_flow_cor_temp = np.resize(z_flow_cor_temp, j - i + 5)
                z_eta_Comp_temp = np.resize(z_eta_Comp_temp, j - i + 5)
                z_pr_temp[j - i + 1] = pres_002
                z_pr_temp[j - i + 2] = pres_003
                z_pr_temp[j - i + 3] = pres_004
                z_pr_temp[j - i + 4] = 0

                z_flow_cor_temp[j - i + 1] = debit_002
                z_flow_cor_temp[j - i + 2] = debit_003
                z_flow_cor_temp[j - i + 3] = debit_004
                z_flow_cor_temp[j - i + 4] = debit_max2

                z_eta_Comp_temp[j - i + 1] = rend_002
                z_eta_Comp_temp[j - i + 2] = rend_003
                z_eta_Comp_temp[j - i + 3] = rend_004
                z_eta_Comp_temp[j - i + 4] = 0.0001

            for u in range(0, self.y_margin.size):
                m = 0
                test = m
                while m <= (z_pr_temp.size-1) and self.y_margin[u] <= (z_pr_temp[test] / pres1):
                    m = m + 1
                    test = min(m, z_pr_temp.size-1)

                if m == 0:
                    l = m

                if m>0 and m<= (z_pr_temp.size -1):
                    l = m - 1

                if m > (z_pr_temp.size -1):
                    l = m - 2

                Txpres1 = z_pr_temp[l]
                Txpres2 = z_pr_temp[l + 1]

                marge1 = (Txpres1 / pres1)
                marge2 = (Txpres2 / pres1)

                Txpres = Txpres2 - ((self.y_margin[u] - marge2) / (marge1 - marge2)) * (Txpres2 - Txpres1)
                self.z_pr[u, k] = max(Txpres, 0)

                deb1 = z_flow_cor_temp[l]
                deb2 = z_flow_cor_temp[l + 1]
                debitr = max(-0.2, deb2 - ((self.y_margin[u] - marge2) / (marge1 - marge2)) * (deb2 - deb1))
                self.z_flow_cor[u, k] = debitr

                rend1 = z_eta_Comp_temp[l]
                rend2 = z_eta_Comp_temp[l + 1]
                rendement = max(0, min(0.9, rend2 - ((self.y_margin[u] - marge2) / (marge1 - marge2)) * (rend2 - rend1)))
                self.z_eta_Comp[u, k] = rendement

            i = j
            k = k + 1
        self.z_pr = self.z_pr[:,0:k]
        self.z_flow_cor = self.z_flow_cor[:, 0:k]
        self.z_eta_Comp = self.z_eta_Comp[:, 0:k]

        self.config['Compr_param']['x_nc'] = self.x_NC
        self.config['Compr_param']['y_margin'] = self.y_margin
        self.config['Compr_param']['surge_pr'] = self.surge_PR
        self.config['Compr_param']['z_pr'] = self.z_pr
        self.config['Compr_param']['z_flow_cor'] = self.z_flow_cor
        self.config['Compr_param']['z_eta_comp'] = self.z_eta_Comp


    def turbine_data(self):
        data_config = self.data.sheet_by_name('Data Turb')
        self.config['Turbine_param']['turbine name'] = data_config.cell_value(0, 1)
        self.config['Turbine_param']['preft'] = data_config.cell_value(3, 1) * 100
        self.config['Turbine_param']['treft'] = data_config.cell_value(4, 1) + 273
        self.config['Turbine_param']['inertia'] = data_config.cell_value(5, 1)
        self.config['Turbine_param']['vol_turbine'] = data_config.cell_value(7, 1)

        'reading initial turbine data'
        deb_col: int = 0
        deb_row: int = 11
        self.field_turb = np.zeros((data_config.nrows - deb_row, 4))
        self.field_turb[:, 0] = data_config.col_values(deb_col, deb_row, data_config.nrows)
        self.field_turb[:, 1] = data_config.col_values(deb_col + 1, deb_row, data_config.nrows)
        self.field_turb[:, 2] = data_config.col_values(deb_col + 2, deb_row, data_config.nrows)
        self.field_turb[:, 2] = self.field_turb[:, 2] * 0.00755
        self.field_turb[:, 3] = data_config.col_values(deb_col + 3, deb_row, data_config.nrows)

        'standardize pressure vector creation'
        incr_rp = 0.05
        max_rp = 5
        min_rp = 1
        self.x_PR = np.linspace(min_rp, max_rp, int((max_rp - min_rp) / incr_rp) + 1)

        i = 0
        k = 0
        self.y_VNTposition = np.array([])
        self.z_pr = np.zeros((self.x_PR.size, int(self.field_turb.size / 4)))
        self.z_flowT_cor = np.zeros((self.x_PR.size, int(self.field_turb.size / 4)))
        self.z_eta_Turb = np.zeros((self.x_PR.size, int(self.field_turb.size / 4)))

        while i < self.field_turb.size / 4:
            'iso_VNT vector'
            self.y_VNTposition = np.resize(self.y_VNTposition, k+1)
            self.y_VNTposition[k] = self.field_turb[i, 0]

            j = i
            test = j
            while j < self.field_turb.size / 4 and self.field_turb[i, 0] == self.field_turb[test, 0]:
                j = j + 1
                test = min(j, self.field_turb.size / 4)


            for u in range(0, self.x_PR.size):
                m = i
                test = m
                while m < (j - 1) and self.x_PR[u] > self.field_turb[test, 1]:
                    m = m + 1
                    test = min(m, j - 1)

                if m == i:
                    l = m

                if m > i and m <= (j - 1):
                    l = m - 1

                if m > (j - 1):
                    l = m - 2

                Txpres1 = self.field_turb[l, 1]
                Txpres2 = self.field_turb[l + 1, 1]

                'calcul du debit'
                deb1 = self.field_turb[l, 2]
                deb2 = self.field_turb[l + 1, 2]
                debitr = max(0, deb1 + ((self.x_PR[u] - Txpres1) / (Txpres2 - Txpres1)) * (
                            deb2 - deb1))
                self.z_flowT_cor[u, k] = debitr

                'calcul du rendement'
                rend1 = self.field_turb[l, 3]
                rend2 = self.field_turb[l + 1, 3]
                rendement = max(0, min(1.5, rend1 + ((self.x_PR[u] - Txpres1) / (Txpres2 - Txpres1)) * (rend2 - rend1)))
                self.z_eta_Turb[u, k] = rendement
            i = j
            k = k + 1

        self.z_flowT_cor = self.z_flowT_cor[:, 0:k]
        self.z_eta_Turb = self.z_eta_Turb[:, 0:k]
        self.config['Turbine_param']['x_pr'] = self.x_PR
        self.config['Turbine_param']['y_vntposition'] = self.y_VNTposition
        self.config['Turbine_param']['z_flowt_cor'] = self.z_flowT_cor
        self.config['Turbine_param']['z_eta_turb'] = self.z_eta_Turb

    def save_model_ini(self):
        file = open("Model_init.ini", "w")
        config_object = ConfigParser()
        sections = self.config.keys()
        for section in sections:
            config_object.add_section(section)
        for section in sections:
            inner_dict = self.config[section]
            fields = inner_dict.keys()
            for field in fields:
                test = inner_dict[field]
                if type(test) == np.ndarray:
                    if test.size / len(test) > 10:
                        value = 'array(['+repr(list(inner_dict[field][0, :]))
                        for i in range(1, max(test.shape[0]-2,2)):
                            value = value + ',\n'+ repr(list(inner_dict[field][i, :]))
                        value = value + ',\n'+ repr(list(inner_dict[field][test.shape[0]-1, :])) + '])'
                    else:
                        value = repr(inner_dict[field])
                else:
                    value = repr(inner_dict[field])
                if value[0] == 'a':
                    value = 'np.' + value
                config_object.set(section, field, value)
        config_object.write(file)
        file.close()

    def save_control_ini(self):
        file = open("Model_control.ini", "w")
        config_object = ConfigParser()
        sections = self.control.keys()
        for section in sections:
            config_object.add_section(section)
        for section in sections:
            inner_dict = self.control[section]
            fields = inner_dict.keys()
            for field in fields:
                value = repr(inner_dict[field])
                if value[0] == 'a':
                    value = 'np.' + value
                config_object.set(section, field, value)
        config_object.write(file)
        file.close()

