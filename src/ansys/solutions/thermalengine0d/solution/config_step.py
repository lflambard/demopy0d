# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Backend of the config step."""

from ansys.saf.glow.solution import StepModel, StepSpec, transaction
import tkinter as tk
from tkinter.filedialog import askopenfilename
from configparser import ConfigParser
from ansys.solutions.thermalengine0d.model.scripts.dataprocess import PreProcess


class ConfigStep(StepModel):
    """Step definition of the config step."""
    first_arg: float = 5
    second_arg: float = 0.001
    third_arg: float = 0.01
    control: dict = {}
    config: dict = {}
    x_N: str = '[]'
    y_N: str = '[]'
    x_pps: str = '[]'
    y_pps: str = '[]'


    @transaction(self=StepSpec(upload=["control","config","x_N", "y_N", "x_pps", "y_pps"],download=["first_arg", "second_arg", "third_arg"]))
    def configure(self) -> None:
        root = tk.Tk()
        root.withdraw()
        name_file = askopenfilename(filetypes=(("Excel file", "*.xls"), ("All Files", "*.*")),
                                    title="Choose a file for Control Configuration."
                                    )
        load_config = PreProcess(name_file)
        load_config.fuel_data()
        load_config.control_data()
        load_config.ecu_data()
        load_config.integrator_data()
        load_config.engine_data()
        load_config.compressor_data()
        load_config.turbine_data()
        load_config.save_model_ini()
        load_config.save_control_ini()
        control1 = ConfigParser()
        control1.read("Model_control.ini")
        config1 = ConfigParser()
        config1.read("Model_init.ini")
        self.control = {s:dict(control1.items(s)) for s in control1.sections()}
        self.config = {s:dict(config1.items(s)) for s in config1.sections()}
        self.x_N = self.control['Engine_control']['x_time_nord']
        self.y_N = self.control['Engine_control']['y_nord']
        self.x_pps = self.control['Engine_control']['x_time_pps']
        self.y_pps = self.control['Engine_control']['y_pps']





