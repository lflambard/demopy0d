# UAV data pre processing from standard excel file
import xlrd
import numpy as np
from configparser import ConfigParser


class PreProcess:

    def __init__(self, filename):
        self.filename = filename
        self.data = xlrd.open_workbook(self.filename)
        self.control = {}
        self.config = {}
        self.control['Uav_control'] = {}
        self.config['Hydro_param'] = {}
        self.config['Propeller_param'] = {}
        self.config['Battery_param'] = {}
        self.config['Motor_param'] = {}
        self.config['Hosepipe_param'] = {}


    def control_data(self):
        data_control = self.data.sheet_by_name('ControlData')
        start_row = 2
        end_row = data_control.nrows
        self.control['Uav_control']['x_time_nord'] = data_control.col_values(0, start_row, end_row)
        self.control['Uav_control']['y_nord'] = data_control.col_values(1, start_row, end_row)

    def hydro_data(self):
        data_config = self.data.sheet_by_name('HydroData')
        self.config['Hydro_param']['config_name'] = data_config.cell_value(0, 1)
        self.config['Hydro_param']['rho_water'] = data_config.cell_value(1, 1)
        self.config['Hydro_param']['nu_water'] = data_config.cell_value(2, 1)
        self.config['Hydro_param']['mass'] = data_config.cell_value(3, 1)
        self.config['Hydro_param']['length'] = data_config.cell_value(4, 1)
        self.config['Hydro_param']['diam'] = data_config.cell_value(5, 1)
        self.config['Hydro_param']['sm'] = data_config.cell_value(6, 1)
        self.config['Hydro_param']['volume'] = data_config.cell_value(7, 1)
        self.config['Hydro_param']['xg'] = data_config.cell_value(8, 1) - data_config.cell_value(10, 1)
        self.config['Hydro_param']['zg'] = data_config.cell_value(9, 1)
        self.config['Hydro_param']['fins_e'] = data_config.cell_value(11, 1)
        self.config['Hydro_param']['fins_c'] = data_config.cell_value(12, 1)
        self.config['Hydro_param']['fins_s'] = data_config.cell_value(13, 1)
        self.config['Hydro_param']['cmbeta'] = data_config.cell_value(14, 1)
        self.config['Hydro_param']['cmw'] = data_config.cell_value(15, 1)
        self.config['Hydro_param']['czbeta'] = data_config.cell_value(16, 1)
        self.config['Hydro_param']['czw'] = data_config.cell_value(17, 1)


    def propeller_data(self):
        data_config = self.data.sheet_by_name('PropellerData')
        self.config['Propeller_param']['kgear'] = data_config.cell_value(0, 1)
        self.config['Propeller_param']['kwake'] = data_config.cell_value(1, 1)
        self.config['Propeller_param']['ksuccion'] = data_config.cell_value(2, 1)
        self.config['Propeller_param']['eta_adaptation'] = data_config.cell_value(3, 1)
        self.config['Propeller_param']['diam_prop'] = data_config.cell_value(4, 1)
        self.config['Propeller_param']['front_rear_ratio'] = data_config.cell_value(5, 1)
        start_col = 1
        end_col = data_config.ncols
        self.config['Propeller_param']['kt_x'] = data_config.row_values(7, start_col, end_col)
        self.config['Propeller_param']['kt_y'] = data_config.row_values(8, start_col, end_col)
        self.config['Propeller_param']['kq_x'] = data_config.row_values(10, start_col, end_col)
        self.config['Propeller_param']['kq_y'] = data_config.row_values(11, start_col, end_col)

    def battery_data(self):
        data_config = self.data.sheet_by_name('BatteryData')
        self.config['Battery_param']['nelements'] = data_config.cell_value(0, 1)
        self.config['Battery_param']['umin'] = data_config.cell_value(1, 1)
        start_col = 1
        end_col = data_config.ncols
        self.config['Battery_param']['y_i'] = data_config.row_values(2, start_col, end_col)
        start_row = 3
        end_row = data_config.nrows
        self.config['Battery_param']['x_capa'] = data_config.col_values(0, start_row, end_row)
        self.MatriceU = np.zeros((end_row - start_row, end_col - start_col), dtype=float)
        for i in range(0, (end_col - start_col)):
            self.MatriceU[:, i] = data_config.col_values(i + start_col, start_row, end_row)
        self.config['Battery_param']['z_u'] = self.MatriceU

    def motor_data(self):
        data_config = self.data.sheet_by_name('MotorData')
        start_col = 1
        end_col = data_config.ncols
        self.config['Motor_param']['x_mot_efficiency'] = data_config.row_values(0, start_col, end_col)
        self.config['Motor_param']['y_mot_efficiency'] = data_config.row_values(1, start_col, end_col)
        end_col = 5
        self.config['Motor_param']['y_u_alpha'] = data_config.row_values(2, start_col, end_col)
        start_row = 3
        end_row = data_config.nrows
        self.config['Motor_param']['x_alpha'] = data_config.row_values(0, start_row, end_row)
        self.MatriceAlpha = np.zeros((end_row - start_row, end_col - start_col))
        for i in range(0, (end_col - start_col)):
            self.MatriceAlpha[:, i] = data_config.col_values(i + start_col, start_row, end_row)
        self.config['Motor_param']['z_alpha_cor'] = self.MatriceAlpha

    def hosepipe_data(self):
        data_config = self.data.sheet_by_name('HosepipeData')
        self.config['Hosepipe_param']['length'] = data_config.cell_value(0, 1)
        start_col = 1
        end_col = data_config.ncols
        self.config['Hosepipe_param']['x_f_hosepipe'] = data_config.row_values(2, start_col, end_col)
        self.config['Hosepipe_param']['y_f_hosepipe'] = data_config.row_values(3, start_col, end_col)

    def save_model_ini(self):
        file = open("ModelUAV_init.ini", "w")
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
        file = open("ModelUAV_control.ini", "w")
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

import tkinter as tk
from tkinter.filedialog import askopenfilename
root = tk.Tk()
root.withdraw()
name_file = askopenfilename(filetypes=(("Excel file", "*.xls"), ("All Files", "*.*")),
                            title="Choose a file for Control Configuration."
                            )
load_config = PreProcess(name_file)
load_config.control_data()
load_config.hydro_data()
load_config.propeller_data()
load_config.battery_data()
load_config.motor_data()
load_config.hosepipe_data()
load_config.save_model_ini()
load_config.save_control_ini()