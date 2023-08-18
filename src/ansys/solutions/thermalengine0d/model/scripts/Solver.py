# Euler Solver
def Integrator_Euler(y_t0, dx, dt):
    y_t1 = y_t0 + dx * dt
    return y_t1

def Integrator(y_t0, dx, dt, dx_prev, method):
    if method == 'Euler':
        y_t1 = y_t0 + dx * dt
    if method == 'Trapezoidal':
        y_t1 = y_t0 + (dx + dx_prev) * dt/2
    return y_t1