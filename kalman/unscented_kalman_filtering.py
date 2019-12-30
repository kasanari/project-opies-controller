import numpy as np
from filterpy.kalman import UnscentedKalmanFilter, MerweScaledSigmaPoints


def init_unscented_kf(loc_data, dt, variance_angular_acc, variance_pos, variance_acc, variance_vel, variance_heading):
    points = MerweScaledSigmaPoints(n=3, alpha=.1, beta=2., kappa=0.)
    ukf = UnscentedKalmanFilter(dim_x=5, dim_z=5, dt=dt, hx=hx, fx=fx, points=points)
    ukf.x = np.array([loc_data.x, loc_data.y, 0.0, 0.0, 0.0])
    ukf.P *= 1

    r = np.zeros((5, 5))
    r[1, 1] = variance_pos  # var x
    r[2, 2] = variance_pos  # var y
    r[3, 3] = variance_acc  # var acc_x
    r[4, 4] = variance_acc  # var acc_y
    r[5, 5] = variance_heading  # var theta
    ukf.R = r

    q = np.zeros((5, 5))
    q[5, 5] = dt * dt * variance_angular_acc  # variance theta = dt^2 * sigma_theta^2
    ukf.Q = q

    return ukf


def fx(x, dt):
    x_out = np.empty_like(x)
    cos_heading = np.cos(x[4])
    sin_heading = np.sin(x[4])

    x_out[0] = x[0] + dt * x[2] * cos_heading + 0.5 * dt * dt * x[3] * cos_heading  # x_(k+1)
    x_out[1] = x[1] + dt * x[2] * sin_heading + 0.5 * dt * dt * x[3] * sin_heading  # y_(k+1)
    x_out[2] = x[2] + dt * x[3]  # v_(k+1)
    x_out[3] = x[3]  # a_(k+1)
    x_out[4] = x[4]  # theta_(k+1)  [theta = heading]
    return x_out


def hx(x):
    z_out = np.empty([1, 5])
    z_out[0] = x[0]
    z_out[1] = x[1]
    z_out[2] = x[3] * np.cos(x[4])
    z_out[3] = x[3] * np.sin(x[4])
    z_out[4] = x[4]
    return z_out
