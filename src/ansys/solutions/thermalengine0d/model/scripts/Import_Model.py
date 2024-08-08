import xlrd


class ImportModel:

    def __init__(self, filename):
        self.filename = filename
        self.data = xlrd.open_workbook(self.filename)
        self.data_model = self.data.sheet_by_name('Model')
        self.model_blocks = ""
        self.model_param = ""
        self.model_solve = ""
        self.model_result_init = ""
        self.model_result = "result_simu[incr_save, 0] = time_simu[i];"

    def Model_creation(self):
        start_row = 2
        end_row = int(self.data_model.cell_value(0, 1)) + start_row
        start_column = 3
        end_col = self.data_model.ncols


        for i in range(start_row, end_row):
            "creation of the blocks"
            self.model_blocks = self.model_blocks + str(self.data_model.cell_value(i, 2)) + "=" + str(self.data_model.cell_value(i, 1)) +"();"

            "param of each block"
            self.model_param = self.model_param + str(self.data_model.cell_value(i, 2)) + ".Param("
            for j in range (start_column, end_col):
                if self.data_model.cell_value(i, j) == '':
                    self.model_param = self.model_param + ");"
                    break
                else:
                    if j+1 >= end_col:
                        self.model_param = self.model_param + str(self.data_model.cell_value(i, j)) + ");"
                        break
                    else:
                        if self.data_model.cell_value(i, j + 1) == '':
                            self.model_param = self.model_param + str(self.data_model.cell_value(i, j)) + ");"
                            break
                        else:
                            self.model_param = self.model_param + str(self.data_model.cell_value(i, j)) + ","

        "connection and running of the model"
        start_row_connect = end_row + 3
        end_row_connect = int(self.data_model.cell_value(start_row_connect - 2, 1)) + start_row_connect

        for k in range(start_row_connect, end_row_connect):
            block = int(self.data_model.cell_value(k, 1)) + start_row - 1
            prev_block = int(self.data_model.cell_value(k, 3)) + start_row - 1


            self.model_solve = self.model_solve + str(self.data_model.cell_value(block, 2)) + "." + str(self.data_model.cell_value(k, 2)) + "=" + str(self.data_model.cell_value(prev_block, 2)) + "." + str(self.data_model.cell_value(k, 4)) + ";"
            if k == end_row_connect-1:
                self.model_solve = self.model_solve + str(self.data_model.cell_value(block, 2)) + ".Solve(step_simu, method);"
            else:
                if int(self.data_model.cell_value(k, 1)) != int(self.data_model.cell_value(k+1, 1)):
                    self.model_solve = self.model_solve + str(self.data_model.cell_value(block, 2)) + ".Solve(step_simu, method);"

        "collecting results"
        start_row_result = end_row_connect + 3
        end_row_result = int(self.data_model.cell_value(start_row_result - 2, 1)) + start_row_result

        self.model_result_init = self.model_result_init + "result_simu = np.zeros((int(LastVal+1 * step_simu / sample_time)," + str(int(self.data_model.cell_value(start_row_result - 2, 1))+1) + ")); result_simu[0, 0] = time_simu[0];"
        for l in range(start_row_result, end_row_result):
            block = int(self.data_model.cell_value(l, 1)) + start_row - 1
            self.model_result_init = self.model_result_init + "result_simu[0," + str(
                int(self.data_model.cell_value(l, 0))) + "] = " + str(self.data_model.cell_value(block, 2)) + "." + str(
                self.data_model.cell_value(l, 2)) + ";"
            self.model_result = self.model_result + "result_simu[incr_save," + str(
                int(self.data_model.cell_value(l, 0))) + "] = " + str(self.data_model.cell_value(block, 2)) + "." + str(
                self.data_model.cell_value(l, 2)) + ";"


