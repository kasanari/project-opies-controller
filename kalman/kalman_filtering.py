from dataclasses import dataclass

import numpy as np
from filterpy.kalman import KalmanFilter

from arduino_interface.imu import IMUData
from kalman.EstimatedState import EstimatedState
from serial_with_dwm.location_data_handler import LocationData
from serial_with_dwm import Measurement


# var_x and var_y in meters
def init_kalman_filter(loc_data, dt,
                       process_var_acc, process_var_vel, process_var_heading,
                       process_var_heading_acc, process_var_pos,
                       meas_var_pos, meas_var_heading, meas_var_acc, speed_div_by_length,
                       use_acc, dim_x, dim_z, dim_u):
    kf = KalmanFilter(dim_x=dim_x, dim_z=dim_z, dim_u=dim_u)
    # init state vector x
    kf.x = set_x(loc_data, use_acc=use_acc)
    kf.F = set_F(dt, use_acc=use_acc)
    kf.H = set_H(use_acc=use_acc)
    kf.B = set_B(speed_div_by_length=speed_div_by_length, use_acc=use_acc)

    kf.P *= 10

    kf.R = set_R(var_acc=meas_var_acc, var_position=meas_var_pos, var_heading=meas_var_heading, use_acc=use_acc)  # measurement noise
    kf.Q = set_Q(dt, var_x=process_var_pos, var_y=process_var_pos, var_acc=process_var_acc,
                 var_heading=process_var_heading, var_heading_acc=process_var_heading_acc,
                 var_velocity=process_var_vel, use_acc=use_acc)  # process noise

    return kf


def set_x(loc_data, use_acc):
    if use_acc:
        x = np.zeros([8,1])
        x[0,0] = loc_data.x
        x[1,0] = loc_data.y
    else:
        x = np.array([[loc_data.x], [loc_data.y], [0.0], [0.0]])  # initialize with first loc_data x and y, 0 in v and a
    return x


def set_F(dt, use_acc=False):
    if use_acc:  # dim_x = 6, dim_z = 4
        f = np.array([[1., 0., 0., 0, dt, 0., 0.5 * dt * dt, 0.],
                      [0., 1., 0., 0., 0., dt, 0., 0.5 * dt * dt],
                      [0., 0., 1., dt, 0., 0., 0., 0.],
                      [0., 0., 0., 1., 0., 0., 0., 0.],
                      [0., 0., 0., 0., 1., 0., dt, 0.],
                      [0., 0., 0., 0., 0., 1., 0., dt],
                      [0., 0., 0., 0., 0., 0., 1., 0.],
                      [0., 0., 0., 0., 0., 0., 0., 1.]]
                     )
    else:
        f = np.array([[1., 0., dt, 0],
                      [0., 1., 0, dt],
                      [0., 0., 1., 0.],
                      [0., 0., 0., 1.]])

    return f


def set_H(use_acc=False):
    if use_acc:
        h = np.array([[1., 0., 0., 0., 0., 0., 0., 0.],
                      [0., 1., 0., 0., 0., 0., 0., 0.],
                      [0., 0., 1., 0., 0., 0., 0., 0.],
                      [0., 0., 0., 0., 0., 0., 1., 0.],
                      [0., 0., 0., 0., 0., 0., 0., 1.]])
    else:
        h = np.array([[1., 0., 0., 0.],
                      [0., 1., 0., 0.]])
    return h


def set_Q(dt, var_heading, var_heading_acc, var_velocity, use_acc = True, var_x=0.0, var_y=0.0,
          var_acc=0.5):  # TODO: prune
    if use_acc:
        var_acc_x = var_acc
        var_acc_y = var_acc
        q = np.array([[var_x, 0., 0., 0., 0., 0., 0., 0.],
                      [0., var_y, 0., 0., 0., 0., 0., 0.],
                      [0., 0., var_heading, 0., 0., 0., 0., 0.],
                      [0., 0., 0., var_heading_acc, 0., 0., 0., 0.],
                      [0., 0., 0., 0., var_velocity, 0., 0., 0.],
                      [0., 0., 0., 0., 0., var_velocity, 0., 0.],
                      [0., 0., 0., 0., 0., 0., var_acc_x, 0.],
                      [0., 0., 0., 0., 0., 0., 0., var_acc_y]
                      ])
    else:  # remove this if acc is good
        var_x_dot = var_velocity
        var_y_dot = var_velocity
        q = np.array([[var_x, 0., 0., 0.],
                      [0., var_y, 0., 0.],
                      [0., 0., var_x_dot, 0.],
                      [0., 0., 0., var_y_dot]])
    return q


def set_B(speed_div_by_length, use_acc):
    if use_acc:
        b = np.zeros([8, 1])
        b[3, 0] = speed_div_by_length
    else:
        b = 0
    return b


def measurement_update(loc_data, imu_data: IMUData, use_acc=False):
    if use_acc:
        z = np.array(
            [[loc_data.x],
             [loc_data.y],
             [imu_data.rotation.yaw],
             [imu_data.world_acceleration.x],
             [imu_data.world_acceleration.y]]
        )
    else:
        z = [[loc_data.x],
             [loc_data.y]]
    return z


def set_R(var_position, var_acc, var_heading, use_acc=False):  # TODO: call this function set_R ?
    var_x = var_position
    var_y = var_position

    if use_acc:
        var_acc_y = var_acc
        var_acc_x = var_acc
        r = np.array([[var_x, 0., 0., 0., 0.],
                      [0., var_y, 0., 0., 0.],
                      [0., 0., var_heading, 0., 0.],
                      [0., 0., 0., var_acc_x, 0.],
                      [0., 0., 0., 0., var_acc_y]])
    else:
        r = np.array([[var_x, 0.],
                      [0., var_y]])
    return r


# # #
# kalman_updates: performs the prediction and update of the Kalman filter
# If the loc_data is None we keep the last z, but we make the covariance matrix for the measurements
# have ~infinity numbers, so the prediction is vastly favored over the measurement.
# Returns: a location estimate as a LocationData
def kalman_updates(kf, loc_data, imu_data: IMUData, timestep, variance_position, variance_acceleration, variance_heading,
                   process_var_heading, process_var_pos, process_var_acc,
                   process_var_heading_acc, process_var_velocity, u=None, use_acc=True):
    kf.F = set_F(timestep, use_acc=use_acc)
    kf.Q = set_Q(timestep, var_x=process_var_pos, var_y=process_var_pos,
                 var_acc=process_var_acc, var_heading=process_var_heading, var_heading_acc=process_var_heading_acc,
                 var_velocity=process_var_velocity, use_acc=use_acc)
    if loc_data is not None:
        z = measurement_update(loc_data, imu_data, use_acc=use_acc)
        kf.R = set_R(var_position=variance_position, var_acc=variance_acceleration, var_heading=variance_heading,
                     use_acc=use_acc)
        loc_quality = loc_data.quality
    else:
        z = kf.z
        kf.R = set_R(var_position=500, var_acc=500, var_heading=500, use_acc=use_acc)  # High value, prefer process model
        loc_quality = -99

    u_rad = np.deg2rad(u[1])

    kf.predict(u=u_rad)
    kf.update(z)

    # Values for estimated state as floats, showing two decimals
    x_kf = float_with_2_decimals(kf.x[0, 0])
    y_kf = float_with_2_decimals(kf.x[1, 0])

    if use_acc:
        yaw_kf = float_with_2_decimals(kf.x[2, 0])
        yaw_acc_kf = float_with_2_decimals(kf.x[3, 0])
        x_v_est = float_with_2_decimals(kf.x[4, 0])
        y_v_est = float_with_2_decimals(kf.x[5, 0])
        x_acc_est = float_with_2_decimals(kf.x[6, 0])
        y_acc_est = float_with_2_decimals(kf.x[7, 0])
    else:
        x_v_est = float_with_2_decimals(kf.x[2, 0])
        y_v_est = float_with_2_decimals(kf.x[3, 0])
        yaw_kf = float_with_2_decimals(0)
        yaw_acc_kf = float_with_2_decimals(0)
        x_acc_est = float_with_2_decimals(0)
        y_acc_est = float_with_2_decimals(0)

    log_likelihood = float_with_2_decimals(kf.log_likelihood)
    likelihood = float_with_2_decimals(kf.likelihood)

    filtered_loc = LocationData(x=x_kf, y=y_kf, z=0, quality=loc_quality)
    estimated_state = EstimatedState(filtered_loc, x_v_est=x_v_est, y_v_est=y_v_est, yaw_est=yaw_kf,
                                     yaw_acc_est=yaw_acc_kf,
                                     log_likelihood=log_likelihood, likelihood=likelihood,
                                     x_acc_est=x_acc_est, y_acc_est=y_acc_est)

    return estimated_state


def float_with_2_decimals(value):
    two_decimal_float = float("{0:.2f}".format(value))
    return two_decimal_float
