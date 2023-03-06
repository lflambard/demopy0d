# ©2022, ANSYS Inc. Unauthorized use, distribution or duplication is prohibited.

"""Solution definition module."""


from ansys.saf.glow.solution import Solution, StepsModel

from ansys.solutions.thermalengine0d.solution.first_step import FirstStep
from ansys.solutions.thermalengine0d.solution.intro_step import IntroStep
from ansys.solutions.thermalengine0d.solution.second_step import SecondStep


class Steps(StepsModel):
    """Workflow definition."""
    intro_step: IntroStep
    first_step: FirstStep
    second_step: SecondStep


class Thermalengine0DSolution(Solution):
    """Solution definition."""
    display_name = "THEngn0D"
    steps: Steps
