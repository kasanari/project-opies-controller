from filterpy.kalman import KalmanFilter
import numpy as np
from serial_with_dwm.location_data_handler import LocationData


# var_x and var_y in meters
def init_kalman_filter(loc_data, dt, angle_vel=0.0, dim_x=4, dim_z=2, dim_u=0, covar_x_y=0.2):
    kf = KalmanFilter(dim_x=dim_x, dim_z=dim_z, dim_u=dim_u)
    # init state vector x
    kf.x = np.array([loc_data.x, loc_data.y, 0.0, 0.0])  # initialize with first loc_data x and y, 0 in velocity
    kf.F = set_F(dt)
    kf.H = np.array([[1., 0., 0., 0.],
                     [0., 1., 0., 0.]])

    if dim_u == 1:
        b = np.array([0., 0., 0., -1])
        kf.B = b.reshape((4, 1))

    distrust_in_value = calculate_distrust(loc_data.quality)
    kf.P *= distrust_in_value

    kf.R = measurement_noise_update(distrust_value=distrust_in_value, covar_x_y=covar_x_y)  # measurement noise
    kf.Q = set_Q(dt)  # process noise TODO should probably change this to reflect the covariance i assume elsewhere

    return kf


def set_F(dt):
    f = np.array([[1., 0., dt, 0],
                  [0., 1., 0, dt],
                  [0., 0., 1., 0.],
                  [0., 0., 0., 1.]])
    return f


def set_F_with_angle(dt):
    pass


def set_Q(dt, acceleleration=True, var_x=0.0, var_y=0.0, var_x_dot=0.0, var_y_dot=0.0,
          covar_xy=0.0, covar_xxdot=0.0, covar_xydot=0.0, covar_yxdot=0.0,
          covar_yydot=0.0, covar_xdotydot=0.0):
    if acceleleration:
        var_x_dot = np.square(dt)
        var_y_dot = np.square(dt)
    q = np.array([[var_x, covar_xy, covar_xxdot, covar_xydot],
                  [covar_xy, var_y, covar_yxdot, covar_yydot],
                  [covar_xxdot, covar_yxdot, var_x_dot, covar_xdotydot],
                  [covar_xydot, covar_yydot, covar_xdotydot, var_y_dot]])
    return q


# calculates the R values. TODO: change this to static error? the quality value is weird.
def calculate_distrust(quality):
    if quality == 0:
        quality = 0.01
    accuracy_UWB_localisation = 0.1  # m
    distrust = accuracy_UWB_localisation + quality/10  # the qualities went higher when we put it in worse conditions??
    # ex measurement: x = 5±0.1 if quality is 100, we want trust_in_measurement to be 1.1
    return distrust

# def init_kalman_filter_angle(loc_data, var_x=0.1, var_y=0.1, covar_x_y=0.2, dt=0.1):
#     kf = KalmanFilter(dim_x=4, dim_z=2)
#     #init state vector x:
#     kf.x = np.array([loc_data.x, loc_data.y, 0.0, 0.0])  # initialize with first loc_data x and y, 0 in velocity
#     kf.F = set_F_angle(dt)
#     kf.H = np.array([[1., 0., 0., 0.],
#                     [0., 1., 0., 0.]])
#     kf.P *= 10/loc_data.quality  # P is a unit matrix. Multiply it with 1/quality factor of first measurement.
#     # Maybe higher value?
#     kf.R = measurement_noise_update(loc_data.quality, var_x=var_x, var_y=var_y, covar_x_y=covar_x_y)
#     q = Q_discrete_white_noise(dim=2, dt=dt, var=0.001)
#     kf.Q = block_diag(q, q)  # process noise x and y
#     #Q =[[0., var, 0., 0.]
#     #   [var, var, 0., 0.]
#     #   [0., 0., 0., var]
#     #   [0., 0., var, var]]
#     return kf


def measurement_update(loc_data):
    z = [[loc_data.x],
        [loc_data.y]]
    return z


def measurement_noise_update(distrust_value, covar_x_y=0.0):  # TODO: changed covar to 0.0, does this affect the result positively?
    var_x = distrust_value
    var_y = distrust_value
    r = np.array([[var_x, covar_x_y],
                  [covar_x_y, var_y]])
    return r

# # #
# kalman_updates: performs the prediction and update of the Kalman filter
# If the loc_data is None we keep the last z, but we make the covariance matrix for the measurements
# have ~infinity numbers, so the prediction is vastly favored over the measurement.
# Returns: a location estimate as a LocationData
def kalman_updates(kf, loc_data, timestep, u=0):
    kf.F = set_F(timestep)
    kf.Q = set_Q(timestep)
    if loc_data is not None:
        z = measurement_update(loc_data)
        distrust_in_measurement = calculate_distrust(loc_data.quality)
        kf.R = measurement_noise_update(distrust_in_measurement)
        #kf.R = measurement_noise_update(50)
        loc_quality = loc_data.quality
    else:
        z = kf.z
        kf.R = measurement_noise_update(0.01)
        loc_quality = -99
    if u < 0:
        u = kf.x[3]  # last y_dot
    kf.predict(u=u)
    kf.update(z)

    x_kf = float("{0:.2f}".format(kf.x[0]))
    y_kf = float("{0:.2f}".format(kf.x[1]))
    filtered_loc = LocationData(x=x_kf, y=y_kf, z=0, quality=loc_quality)

    return filtered_loc  
