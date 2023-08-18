# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Backend of the second step."""


from ansys.saf.glow.solution import StepModel, StepSpec, transaction
from typing import List
from ansys.solutions.thermalengine0d.solution.first_step import FirstStep
import pandas as pd
import tkinter as tk
from tkinter.filedialog import asksaveasfilename

class SecondStep(StepModel):
    """Step definition of the second step."""
    result: float = 0
    x_coord : List[float] = []
    y_coord: dict = {}
    id: str = "hey"

    @transaction(self=StepSpec(upload=["result", "x_coord", "y_coord"]), first_step=StepSpec(download=["result_simu"]))
    def plots(self, first_step: FirstStep):
        self.result = 0
        self.x_coord = first_step.result_simu['time']
        self.y_coord = first_step.result_simu

    @transaction(first_step=StepSpec(download=["result_simu"]))
    def exportcsv(self, first_step: FirstStep):
        data = pd.DataFrame(first_step.result_simu)
        root = tk.Tk()
        root.withdraw()
        name_save= asksaveasfilename(defaultextension='xlsx')
        if name_save:
            data.to_excel(name_save, sheet_name='Simulation Results', index=False)

