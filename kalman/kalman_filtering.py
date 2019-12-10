from filterpy.kalman import KalmanFilter
import numpy as np
from serial_with_dwm.location_data_handler import LocationData
from dataclasses import dataclass
from arduino_interface.imu import IMUData, Transform

@dataclass
class EstimatedState:
    location_est: LocationData
    x_v_est: float
    y_v_est: float
#    x_acc_est: float
#    y_acc_est: float


# var_x and var_y in meters
def init_kalman_filter(loc_data, dt, use_acc=True, dim_x=6, dim_z=4, dim_u=0, covar_x_y=0.2):
    kf = KalmanFilter(dim_x=dim_x, dim_z=dim_z, dim_u=dim_u)

    # init state vector x
    kf.x = set_x(loc_data, use_acc=use_acc)
    kf.F = set_F(dt, use_acc=use_acc)
    kf.H = set_H(use_acc=use_acc)
    kf.B = set_B(dim_u)  # only functional for x_dim = 4 right now

    distrust_in_value = calculate_distrust(loc_data.quality)
    kf.P *= distrust_in_value

    kf.R = measurement_noise_update(distrust_value=distrust_in_value, covar_x_y=covar_x_y, use_acc=use_acc)  # measurement noise
    kf.Q = set_Q(dt, use_acc=use_acc)  # process noise

    return kf


def set_x(loc_data, use_acc):
    if use_acc:
        x = np.array([loc_data.x, loc_data.y, 0.0, 0.0, 0.0, 0.0])
    else:
        x = np.array([loc_data.x, loc_data.y, 0.0, 0.0])  # initialize with first loc_data x and y, 0 in v and a
    return x


def set_F(dt, use_acc=False):
    if use_acc:  # dim_x = 6, dim_z = 4
        f = np.array([[1., 0., dt, 0, dt * dt, 0],
                      [0., 1., 0., dt, 0., dt * dt],
                      [0., 0., 1., 0., 0., 0.],
                      [0., 0., 0., 1., 0., 0.],
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
          covar_xy=0.0, covar_xxdot=0.0, covar_xydot=0.0, covar_yxdot=0.0,
          covar_yydot=0.0, covar_xdotydot=0.0):
    if use_acc:
        var_acc_x = 0.5
        var_acc_y = var_acc_x
        q = np.array([[var_x, 0., 0., 0., 0., 0.],
                      [0., var_y, 0., 0., 0., 0.],
                      [0., 0., dt * dt, 0., 0., 0.],
                      [0., 0., 0., dt * dt, 0., 1.],
                      [0., 0., 0., 0., var_acc_x, 0.],
                      [0., 0., 0., 0., 0., var_acc_y]
                      ])
    else: # remove this if acc is good
        if acceleleration:
            var_x_dot = np.square(dt)
            var_y_dot = np.square(dt)
        q = np.array([[var_x, covar_xy, covar_xxdot, covar_xydot],
                      [covar_xy, var_y, covar_yxdot, covar_yydot],
                      [covar_xxdot, covar_yxdot, var_x_dot, covar_xdotydot],
                      [covar_xydot, covar_yydot, covar_xdotydot, var_y_dot]])
    return q


def set_B(dim_u):
    if dim_u == 0:
        b = None
    elif dim_u == 1:
        b = np.array([[0.],
                     [0.],
                     [0.],
                     [1]])
    elif dim_u == 2:
        b = np.array([[0., 0.],
                     [0., 0.],
                     [0., 0.],
                     [1, 0.]])
    else:
        print("I don't have a model for these control signals/this dim_u. Treating dim_u as 0.")
        b = None
    return b


# calculates the R values. TODO: change this to static error? the quality value is weird.
def calculate_distrust(quality):
    if quality == 0:
        quality = 0.01
    accuracy_UWB_localisation = 0.1  # m
    distrust = accuracy_UWB_localisation + (100-quality)/10  # the qualities went higher when we put it in worse conditions??
    # ex measurement: x = 5±0.1 if quality is 100, we want trust_in_measurement to be 1.1
    return distrust


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


def measurement_noise_update(distrust_value, covar_x_y=0.0, use_acc=False):  # TODO: changed covar to 0.0, does this affect the result positively?
    var_x = distrust_value
    var_y = distrust_value

    if use_acc:
        var_acc_y = 10
        var_acc_x = 10
        r = np.array([[var_x, 0., 0., 0.],
                      [0., var_y, 0., 0.],
                      [0., 0., var_acc_x, 0.],
                      [0., 0., 0., var_acc_y]])
    else:
        r = np.array([[var_x, covar_x_y],
                      [covar_x_y, var_y]])
    return r

# # #
# kalman_updates: performs the prediction and update of the Kalman filter
# If the loc_data is None we keep the last z, but we make the covariance matrix for the measurements
# have ~infinity numbers, so the prediction is vastly favored over the measurement.
# Returns: a location estimate as a LocationData
def kalman_updates(kf, loc_data, imu_data, timestep, u=None, use_acc=True):
    kf.F = set_F(timestep, use_acc=use_acc)
    kf.Q = set_Q(timestep, use_acc=use_acc)
    if loc_data is not None:
        z = measurement_update(loc_data, imu_data, use_acc=use_acc)
        distrust_in_measurement = calculate_distrust(loc_data.quality)
        kf.R = measurement_noise_update(distrust_in_measurement, use_acc=use_acc)
        loc_quality = loc_data.quality
    else:
        z = kf.z
        kf.R = measurement_noise_update(1000)  # High value, prefer process model
        loc_quality = -99
    if u is not None:
        if u < 0:
            u = kf.x[3]  # last y_dot.  # TODO: for u=u_steering, controlling y_dot only. Change if changed!!
    kf.predict(u=u)
    kf.update(z)

    x_kf = float("{0:.2f}".format(kf.x[0]))
    y_kf = float("{0:.2f}".format(kf.x[1]))
    x_velocity = float("{0:.2f}".format(kf.x[2]))
    y_velocity = float("{0:.2f}".format(kf.x[3]))
    filtered_loc = LocationData(x=x_kf, y=y_kf, z=0, quality=loc_quality)
    estimated_state = EstimatedState(filtered_loc, x_v_est=x_velocity, y_v_est=y_velocity)

    return estimated_state
