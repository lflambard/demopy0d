# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Backend of the second step."""


from ansys.saf.glow.solution import StepModel, StepSpec, transaction
import numpy as np
import matplotlib.pyplot as plt

class SecondStep(StepModel):
    """Step definition of the second step."""
    first_arg: float = 0
    second_arg: float = 0
    result: float = 0
    id: str = "hey"

    @transaction(self=StepSpec(upload=["result"], download=["first_arg", "second_arg"]))
    def plots(self):
        self.result = self.first_arg + self.second_arg
        self.x = np.array([0, self.first_arg])
        self.y = np.array([self.second_arg, 5])
        plt.plot(self.x, self.y)
        plt.show()


