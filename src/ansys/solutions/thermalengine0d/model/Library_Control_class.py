#Control Library
# Contains:
#   - PI_control (anti saturated)
#   - PID control (anti saturated)
#   - Electric Motor Control
#   - UAV supervisor
import math

from ansys.solutions.thermalengine0d.model.scripts.Solver import Integrator_Euler, Integrator
from ansys.solutions.thermalengine0d.model.scripts.Signal_treatment import relay, rate_limiter, derivative
from ansys.solutions.thermalengine0d.model.scripts.Data_treatment import interpolv


"------------------------------------------------------------------------"
"PI Controller (with anti saturation)"
"------------------------------------------------------------------------"

class PI_control:
    def __init__(self, x_Ord, x_Act, y0=0, Ki_eps=0):
        self.x_Ord = x_Ord
        self.x_Act = x_Act
        self.y = y0
        self.Ki_eps = 0
        self.eps = 0

    def Param(self, Kp, Ki, x_min, x_max):
        self.Kp = Kp
        self.Ki = Ki
        self.x_min = x_min
        self.x_max = x_max

    def Solve(self, dt, method='Euler'):
        Kp_eps = self.Kp * (self.x_Ord - self.x_Act)
        self.y = max(self.x_min, min(self.x_max, Kp_eps + self.Ki_eps))
        self.eps_prev = self.eps
        self.eps = self.Ki * (self.y - self.Ki_eps)
        self.Ki_eps = Integrator(self.Ki_eps, self.eps, dt, self.eps_prev, method)

"------------------------------------------------------------------------"
"PID Controller (with anti saturation)"
"------------------------------------------------------------------------"

class PID_control:
    def __init__(self, x_Ord, x_Act, y0=0, Ki_eps=0):
        self.x_Ord = x_Ord
        self.x_Act = x_Act
        self.y = y0
        self.Ki_eps = 0
        self.eps = 0
        self.eps_prev = self.eps
        self.d_eps = self.x_Ord - self.x_Act

    def Param(self, Kp, Ki, x_min, x_max, Kd=0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.x_min = x_min
        self.x_max = x_max

    def Solve(self, dt, method='Euler'):
        Kp_eps = self.Kp * (self.x_Ord - self.x_Act)
        Kd_eps = self.Kd * derivative(self.x_Ord - self.x_Act, self.d_eps, dt)
        self.y = max(self.x_min, min(self.x_max, Kp_eps + self.Ki_eps + Kd_eps))
        self.d_eps = self.x_Ord - self.x_Act
        self.eps_prev = self.eps
        self.eps = self.Ki * (self.y - self.Ki_eps)
        self.Ki_eps = Integrator(self.Ki_eps, self.eps, dt, self.eps_prev, method)


"------------------------------------------------------------------------"
"Emotor Controller (current and angle control)"
"------------------------------------------------------------------------"
class EMotorControl:
    def __init__(self, N_ord, N_act, I_ord0=0, Alpha_mot0=0):
        self.N_ord = N_ord
        self.N_act = N_act
        self.I_ord = I_ord0
        self.alpha_mot = Alpha_mot0
        self.Ki_eps_I = 0
        self.Ki_eps_Alpha = 0

    def Param(self, Flag_mot=0, relay_control=0, Nmot_ord_incr=0, Nmot_ord_lim=0):
        self.Flag_mot = Flag_mot
        self.relay_control = relay_control
        self.Nmot_ord_incr = Nmot_ord_incr
        self.Nmot_ord_lim = Nmot_ord_lim

    def Solve(self, dt, method='Euler'):

        'ramp function'
        self.relay_control = relay(self.relay_control, self.N_ord, 2000, 959)
        if self.relay_control == 0:
            self.N_ord_LSTE = 0
        else:
            self.N_ord_LSTE = self.N_ord

        if self.N_ord_LSTE <= 2000:
            self.Nmot_ord_lim = self.N_act

        Nlim = max(0, self.Nmot_ord_lim)

        if self.N_ord_LSTE >= Nlim:
            self.Nmot_ord_incr = rate_limiter(self.Nmot_ord_incr, self.N_ord_LSTE - Nlim, 2250, -820 * 1.35, dt)
            self.Nmot_ord_PCU = Nlim + self.Nmot_ord_incr
        else:
            self.Nmot_ord_PCU = self.N_ord_LSTE

        self.Flag_mot = relay(self.Flag_mot, self.Nmot_ord_PCU, 13360, 13000)

        if self.Flag_mot >= 1:
            Nmot_ord_I = self.N_act
            Nmot_ord_Alpha = self.Nmot_ord_PCU
        else:
            Nmot_ord_I = self.Nmot_ord_PCU
            Nmot_ord_Alpha = self.N_act

        'PI Current'
        Kp_I = 0.0349
        Ki_I = 0.2058
        Kp_eps_I = Kp_I * (Nmot_ord_I - self.N_act)
        Imax_PI = 380
        Imin_PI = 0
        Imax_ord = 450
        Imin_ord = 0
        if (self.Ki_eps_I + Kp_eps_I) < Imin_PI or (self.Ki_eps_I + Kp_eps_I) > Imax_PI:
            eps_I = 0
        else:
            eps_I = Ki_I * (Nmot_ord_I - self.N_act)
        self.Ki_eps_I_prev = self.Ki_eps_I
        self.Ki_eps_I = Integrator(self.Ki_eps_I, eps_I, dt, self.Ki_eps_I_prev, method)

        'PI Alpha'
        Alpha_0 = 21
        Alpha_min_PI = 21 - 50
        Alpha_max_PI = 21
        Kp_Alpha = 0.0022
        Ki_alpha = 0.0282
        Kp_eps_Alpha = Kp_Alpha * (Nmot_ord_Alpha - self.N_act)
        if (self.Ki_eps_Alpha + Kp_eps_Alpha) < Alpha_min_PI or (self.Ki_eps_Alpha + Kp_eps_Alpha) > Alpha_max_PI:
            eps_Alpha = 0
        else:
            eps_Alpha = Ki_alpha * (Nmot_ord_Alpha - self.N_act)
        self.Ki_eps_Alpha_prev = self.Ki_eps_Alpha
        self.Ki_eps_Alpha = Integrator(self.Ki_eps_Alpha, eps_Alpha, dt, self.Ki_eps_Alpha_prev, method)

        if self.relay_control == 1:
            if self.Flag_mot < 1:
                self.I_ord = max(Imin_PI, min(Imax_PI, self.Ki_eps_I + Kp_eps_I))
                self.alpha_mot = 21
            else:
                self.alpha_mot = Alpha_0 - max(Alpha_min_PI, min(Alpha_max_PI, self.Ki_eps_Alpha + Kp_eps_Alpha))
                if self.alpha_mot <= (Alpha_0 - Alpha_max_PI):
                    self.I_ord = min(Imax_ord, Integrator_Euler(self.I_ord, 53, dt))
                else:
                    if self.alpha_mot >= (Alpha_0 - Alpha_min_PI):
                        self.I_ord = max(Imin_ord, Integrator_Euler(self.I_ord, -53, dt))
                    else:
                        self.I_ord = self.I_ord
        else:
            self.Ki_eps_I = 0
            self.Ki_eps_Alpha = 0
            self.I_ord = 0


"------------------------------------------------------------------------"
"UAV Supervisor"
"------------------------------------------------------------------------"
class UavSupervisor:
    def __init__(self, N_act, N_ord,  U, Psi_act=0, Psi_ord=0, Z_act=0, Z_ord=0, Theta_act=0, Phi_act=0, Phi_ord=0, Nmot_lim_LSTE=0):
        self.N_act = N_act
        self.N_ord = N_ord
        self.Psi_act = Psi_act
        self.Psi_ord = Psi_ord
        self.Z_act = Z_act
        self.Z_ord = Z_ord
        self.Theta_act = Theta_act
        self.Phi_act = Phi_act
        self.Phi_ord = Phi_ord
        self.U = U
        self.Nmot_lim_LSTE = Nmot_lim_LSTE
        self.N_act_prev = N_act
        self.Theta_act_prev = Theta_act
        self.Ki_eps_theta = 0
        self.eps = 0
        self.Rudders = [0, 0, 0, 0]

    def Param(self, Kspeed, Flag_U=0):
        self.Kspeed = Kspeed
        self.Flag_U = Flag_U

    def Solve(self, dt, time, method='Euler'):
        if time <= 50:
            self.Flag_U = relay(self.Flag_U, self.U, 194, 190)
            if self.Flag_U == 1:
                self.Nmot_ord = self.N_ord
                self.Nmot_lim_LSTE = self.N_act
            else:
                self.Nmot_ord = self.Nmot_lim_LSTE
        else:
            self.Nmot_ord = rate_limiter(self.Nmot_ord, self.N_ord, 875, -20000, dt)

        self.V_ord = self.N_ord * self.Kspeed

        'Alpha Controller'
        Kp_alpha = 1.2
        Kd_alpha = -0.5
        alpha_min = -19 * math.pi / 180
        alpha_max = 19 * math.pi / 180
        eps_alpha = self.Psi_ord - self.Psi_act

        if (abs(eps_alpha - math.pi)<= 1e-2 or abs(math.fmod(eps_alpha, 2 * math.pi))<=abs(math.fmod(eps_alpha, -2 * math.pi))) and abs(eps_alpha + math.pi) > 1e-2:
            self.alpha_ord = max(alpha_min,min(alpha_max, Kp_alpha * math.fmod(eps_alpha, 2 * math.pi)
                                               + Kd_alpha * derivative(self.N_act, self.N_act_prev, dt)))
        else:
            self.alpha_ord = max(alpha_min, min(alpha_max, Kp_alpha * math.fmod(eps_alpha, -2 * math.pi)
                                                + Kd_alpha * derivative(self.N_act, self.N_act_prev, dt)))
        self.N_act_prev = self.N_act

        'Beta Controller'
        eps_theta = self.Z_ord - self.Z_act
        if eps_theta <= 31:
            flag_control = 1
        else:
            flag_control = 0

        if flag_control == 1:
            Kp_theta = interpolv([0, 8000, 11000, 12000, 16000], [-0.04, -0.0233, -0.0233, -0.018, -0.016], self.N_act) * 0.8
        else:
            Kp_theta = interpolv([0, 8000, 11000, 12000, 16000], [-0.04, -0.0233, -0.0233, -0.018, -0.016], self.N_act) * 1.15
        Ki_theta = 0.5
        theta_min = -45 * math.pi / 180
        theta_max = 45 * math.pi / 180
        Kp_eps = Kp_theta * eps_theta
        self.Theta_ord = max(theta_min, min(theta_max, Kp_eps + self.Ki_eps_theta))
        self.eps_prev = self.eps
        if abs(eps_theta) >= 0.5:
            self.eps = Ki_theta * (self.Theta_ord - self.Ki_eps_theta)
        else:
            self.eps = Ki_theta * (0 - self.Ki_eps_theta)
        self.Ki_eps_theta = Integrator(self.Ki_eps_theta, self.eps, dt, self.eps_prev, method)

        Kp_beta = interpolv([0, 8000, 11000, 12000, 16000], [-6.1, -3.1, -3.1, -1.8, -1.2], self.N_act)
        Kd_beta = interpolv([0, 8000, 11000, 12000, 16000], [1.8, 1.2, 1.2, 0.8, 0.6], self.N_act) * 0.5
        eps_beta = self.Theta_ord - self.Theta_act
        beta_min = -20 * math.pi / 180
        beta_max = 20 * math.pi / 180
        self.beta_ord = max(beta_min, min(beta_max, Kp_beta * eps_beta
                            + Kd_beta * derivative(self.Theta_act, self.Theta_act_prev, dt)))
        self.Theta_act_prev = self.Theta_act

        'gamma controller'
        if time > 7 and abs(self.Phi_ord - self.Phi_act) <= 30 * math.pi/180:
            Kp_gamma = interpolv([8000, 16000], [1, 0.15], self.N_act) * 0.04
            Ki_gamma = 1.3
            gamma_max = -0.6 * math.pi/180
            gamma_min = -4 * math.pi/180
        else:
            Kp_gamma = interpolv([8000, 16000], [1, 0.2], self.N_act) * 0.5
            Ki_gamma = 0.1
            gamma_max = 4 * math.pi / 180
            gamma_min = -8 * math.pi / 180
        gamma_PID = PID_control(self.Phi_ord, self.Phi_act)
        gamma_PID.Param(Kp_gamma, Ki_gamma, gamma_min, gamma_max, 0)
        gamma_PID.Solve(dt, method)
        self.gamma_ord = gamma_PID.y

        'Rudders allocation'
        self.Rudders[0] = max(-20 * math.pi / 180, min(20 * math.pi / 180, self.alpha_ord - self.gamma_ord))
        self.Rudders[1] = max(-20 * math.pi / 180, min(20 * math.pi / 180, self.alpha_ord + self.gamma_ord))
        self.Rudders[2] = max(-20 * math.pi / 180, min(20 * math.pi / 180, -self.beta_ord - self.gamma_ord))
        self.Rudders[3] = max(-20 * math.pi / 180, min(20 * math.pi / 180, -self.beta_ord + self.gamma_ord))





