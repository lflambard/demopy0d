
from ansys.solutions.thermalengine0d.model.scripts.Solver import Integrator_Euler

   
#First Order
def first_order(FO_Out_t0, FO_In, FO_Out_Init, Tau, dt):
    Delta_FO = (FO_In - FO_Out_t0) / Tau
    FO_Out_t1 = FO_Out_Init + Integrator_Euler(FO_Out_t0 - FO_Out_Init, Delta_FO, dt)
    return FO_Out_t1


#Rate limiter
def rate_limiter(RL_Out_t0, RL_In, Rising_rate, Falling_rate, dt):

    ratio = (RL_In - RL_Out_t0) / dt

    if ratio > Rising_rate:
        RL_Out_t1 = dt * Rising_rate + RL_Out_t0
    else:
        if ratio < Falling_rate:
            RL_Out_t1 = dt * Falling_rate + RL_Out_t0
        else:
            RL_Out_t1 = RL_In
    
    return RL_Out_t1


#Relay (Switch)
def relay(SW_output, SW_input, SW_on_point, SW_off_point):

    if SW_output <= 0 and SW_input >= SW_on_point:
        relay = 1
    else:
        relay = SW_output

    if relay >= 1 and SW_input <= SW_off_point:
        relay = 0

    return relay


#Derivative
def derivative(x, x_prev, dt):
    y = (x - x_prev) / dt
    return y


