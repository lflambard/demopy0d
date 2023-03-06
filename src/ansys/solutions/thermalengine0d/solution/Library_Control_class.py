#Control Library
# Contains:
#   - PI_control (anti saturated)

from ansys.solutions.thermalengine0d.solution.Solver import Integrator_Euler

"------------------------------------------------------------------------"
"PI Controller (with anti saturation)"
"------------------------------------------------------------------------"

class PI_control:
    def __init__(self, x_Ord, x_Act, y0=0, Ki_eps=0):
        self.x_Ord = x_Ord
        self.x_Act = x_Act
        self.y = y0
        self.Ki_eps=0

    def Param(self, Kp, Ki, x_min, x_max):
        self.Kp = Kp
        self.Ki = Ki
        self.x_min = x_min
        self.x_max = x_max

    def Solve(self, dt):
        Kp_eps = self.Kp * (self.x_Ord - self.x_Act)
        self.y = max(self.x_min, min(self.x_max, Kp_eps + self.Ki_eps))
        eps = self.Ki * (self.y - self.Ki_eps)
        self.Ki_eps = Integrator_Euler(self.Ki_eps, eps, dt)


