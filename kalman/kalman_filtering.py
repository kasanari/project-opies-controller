from dataclasses import dataclass

import numpy as np
from filterpy.kalman import KalmanFilter

from arduino_interface.imu import IMUData
from kalman.EstimatedState import EstimatedState
from serial_with_dwm.location_data_handler import LocationData
from serial_with_dwm import Measurement

@dataclass
class EstimatedState:
    location_est: LocationData
    x_v_est: float
    y_v_est: float
    log_likelihood: float
    likelihood: float
    x_acc_est: float
    y_acc_est: float
    measurement: Measurement = None


# var_x and var_y in meters
def init_kalman_filter(loc_data, dt, use_acc=True, dim_x=6, dim_z=4, dim_u=0, variance_position=0.2,
                       variance_acc=0.8, variance_velocity=0.8):
    kf = KalmanFilter(dim_x=dim_x, dim_z=dim_z, dim_u=dim_u)
    init_yaw = 0
    # init state vector x
    kf.x = set_x(loc_data, use_acc=use_acc)
    kf.F = set_F(dt, yaw=init_yaw, use_acc=use_acc)
    kf.H = set_H(use_acc=use_acc)
    kf.B = set_B(dim_u)  # only functional for x_dim = 4 right now

    kf.P *= variance_position

    kf.R = measurement_noise_update(var_acc=variance_acc, var_position=variance_position, use_acc=use_acc)  # measurement noise
    kf.Q = set_Q(dt, var_velocity=variance_velocity, var_acc=variance_acc, use_acc=use_acc)  # process noise

    return kf


def set_x(loc_data, use_acc):
    if use_acc:
        x = np.array([loc_data.x, loc_data.y, 0.0, 0.0, 0.0, 0.0])
    else:
        x = np.array([loc_data.x, loc_data.y, 0.0, 0.0])  # initialize with first loc_data x and y, 0 in v and a
    return x


def set_F(dt, yaw, use_acc=False):
    if use_acc:  # dim_x = 6, dim_z = 4
        f = np.array([[1., 0., dt, 0, (dt * dt) / 2, 0],
                      [0., 1., 0., dt, 0., (dt * dt) / 2],
                      [0., 0., 1., 0., dt, 0.],
                      [0., 0., 0., 1., 0., dt],
                      [0., 0., 0., 0., 1., 0.],
                      [0., 0., 0., 0., 0., 1.]]
                     )
    else:
        f = np.array([[1., 0., dt, 0],
                      [0., 1., 0, dt],
                      [0., 0., 1., 0.],
                      [0., 0., 0., 1.]])

    return f


def set_F_with_angle(dt):
    pass


def set_H(use_acc=False):
    if use_acc:
        h = np.array([[1., 0., 0., 0., 0., 0.],
                      [0., 1., 0., 0., 0., 0.],
                      [0., 0., 0., 0., 1., 0.],
                      [0., 0., 0., 0., 0., 1.]])
    else:
        h = np.array([[1., 0., 0., 0.],
                      [0., 1., 0., 0.]])
    return h


def set_Q(dt, use_acc = True, acceleleration=True, var_x=0.0, var_y=0.0, var_x_dot=0.0, var_y_dot=0.0,
          var_acc=0.5, var_velocity=0.5):  # TODO: prune
    if use_acc:
        var_acc_x = var_acc
        var_acc_y = var_acc
        var_v_x = var_velocity
        var_v_y = var_velocity
        q = np.array([[var_x, 0., 0., 0., 0., 0.],
                      [0., var_y, 0., 0., 0., 0.],
                      [0., 0., var_v_x, 0., 0., 0.],
                      [0., 0., 0., var_v_y, 0., 0.],
                      [0., 0., 0., 0., var_acc_x, 0.],
                      [0., 0., 0., 0., 0., var_acc_y]
                      ])
    else:  # remove this if acc is good
        if acceleleration:
            var_x_dot = np.square(dt)
            var_y_dot = np.square(dt)
        q = np.array([[var_x, 0., 0., 0.],
                      [0., var_y, 0., 0.],
                      [0., 0., var_x_dot, 0.],
                      [0., 0., 0., var_y_dot]])
    return q


def set_B(dim_u, use_acc=True):
    if dim_u == 0:
        b = None
    elif dim_u == 1:
        b = np.array([[0.],
                      [0.],
                      [0.],
                      [1]])

    elif dim_u == 2:
        if use_acc:
            b = np.array([[0., 0.],
                         [0., 0.],
                         [0., 0.],
                         [10, 0.],  # estimate_y_dot = estimate_y_dot + 10 * u_speed (0.16 ≤ u_speed ≤ 0.18)
                          [0., 0.],
                          [0., 0.]])

        else:
            b = np.array([[0., 0.],
                          [0., 0.],
                          [0., 0.],
                          [1, 0.]])

    else:
        print("I don't have a model for these control signals/this dim_u. Treating dim_u as 0.")
        b = None
    return b


def measurement_update(loc_data, imu_data: IMUData, use_acc=False):
    if use_acc:
        acc_y = imu_data.real_acceleration.y
        acc_x = imu_data.real_acceleration.x

        z = [[loc_data.x],
             [loc_data.y],
             [acc_x],
             [acc_y]]
    else:
        z = [[loc_data.x],
             [loc_data.y]]
    return z


def measurement_noise_update(var_position, var_acc, use_acc=False):  # TODO: call this function set_R ?
    var_x = var_position
    var_y = var_position

    if use_acc:
        var_acc_y = var_acc
        var_acc_x = var_acc
        r = np.array([[var_x, 0., 0., 0.],
                      [0., var_y, 0., 0.],
                      [0., 0., var_acc_x, 0.],
                      [0., 0., 0., var_acc_y]])
    else:
        r = np.array([[var_x, 0.],
                      [0., var_y]])
    return r


# # #
# kalman_updates: performs the prediction and update of the Kalman filter
# If the loc_data is None we keep the last z, but we make the covariance matrix for the measurements
# have ~infinity numbers, so the prediction is vastly favored over the measurement.
# Returns: a location estimate as a LocationData
def kalman_updates(kf, loc_data, imu_data: IMUData, timestep, variance_position, variance_acceleration,
                   u=None, use_acc=True):
    kf.F = set_F(timestep, yaw=imu_data.rotation.yaw, use_acc=use_acc)
    kf.Q = set_Q(timestep, use_acc=use_acc)
    if loc_data is not None:
        z = measurement_update(loc_data, imu_data, use_acc=use_acc)
        kf.R = measurement_noise_update(var_position=variance_position, var_acc=variance_acceleration,
                                        use_acc=use_acc)
        loc_quality = loc_data.quality
    else:
        z = kf.z
        kf.R = measurement_noise_update(var_position=500, var_acc=500, use_acc=use_acc)  # High value, prefer process model
        loc_quality = -99
    if u is not None:
        if u[0] < 0:
            u[0] = kf.x[3]  # last y_dot.  # TODO: for u=u_steering, controlling y_dot only. Change if changed!!
    kf.predict(u=u)
    kf.update(z)

    # Values for estimated state as floats, showing two decimals
    x_kf = float_with_2_decimals(kf.x[0])
    y_kf = float_with_2_decimals(kf.x[1])
    x_velocity = float_with_2_decimals(kf.x[2])
    y_velocity = float_with_2_decimals(kf.x[3])
    log_likelihood = float_with_2_decimals(kf.log_likelihood)
    likelihood = float_with_2_decimals(kf.likelihood)
    x_acceleration = float_with_2_decimals(kf.x[4])
    y_acceleration = float_with_2_decimals(kf.x[5])

    filtered_loc = LocationData(x=x_kf, y=y_kf, z=0, quality=loc_quality)
    estimated_state = EstimatedState(filtered_loc, x_v_est=x_velocity, y_v_est=y_velocity,
                                     log_likelihood=log_likelihood, likelihood=likelihood,
                                     x_acc_est=x_acceleration, y_acc_est=y_acceleration)

    return estimated_state


def float_with_2_decimals(value):
    two_decimal_float = float("{0:.2f}".format(value))
    return two_decimal_float
