from filterpy.kalman import KalmanFilter, ExtendedKalmanFilter
from filterpy.common import Q_discrete_white_noise
import numpy as np
from scipy.linalg import block_diag
from location_data_handler import LocationData

# class KalmanHelper:
#
#     def __init__(self, loc_data):
#         self.x_vector = np.array(loc_data.x)
#         self.x_dot = np.array([0])
#         self.y_vector = np.array(loc_data.y)
#         self.y_dot = np.array([0])
#         self.state_vector = np.array(self.x_vector, self.y_vector, self.x_dot, self.y_dot)  # state vector. in KF
#         # theory, called x
#
#     def update_loc_vectors(self, loc_data):
#         self.x_vector = np.append(self.x_vector, loc_data.x)
#         self.y_vector = np.append(self.y_vector, loc_data.y)
#
#     def update_velocities(self, past_loc, current_loc, delta):
#         new_x_dot = (current_loc.x-past_loc.x)/delta
#         new_y_dot = (current_loc.y-past_loc.y)/delta
#         self.x_dot = np.append(self.x_dot, new_x_dot)
#         self.y_dot = np.append(self.y_dot, new_y_dot)
#
#     def update_state_vector(self):
#         self.state_vector = np.array(self.x_vector, self.y_vector, self.x_dot, self.y_dot)


# var_x and var_y in meters
def init_kalman_filter(loc_data, dt, covar_x_y=0.2):
    kf = KalmanFilter(dim_x=4, dim_z=2)  
    # init state vector x: [x, y, x_dot, y_dot]
    kf.x = np.array([loc_data.x, loc_data.y, 0.0, 0.0])  # initialize with first loc_data x and y, 0 in velocity
    kf.F = np.array([[1., 0., dt, 0],
                    [0., 1., 0, dt],
                    [0., 0., 1., 0.],
                    [0., 0., 0., 1.]])
    kf.H = np.array([[1., 0., 0., 0.],
                    [0., 1., 0., 0.]])
    distrust_in_value = calculate_distrust(loc_data.quality)
    kf.P *= distrust_in_value

    # P is a unit matrix. Multiply it with quality factor of first measurement. Maybe higher value?
      # measurement noise. not sure what values to put here.
    kf.R = measurement_noise_update(distrust_value=distrust_in_value, covar_x_y=covar_x_y)
    #kf.R = measurement_noise_update(distrust_value=5, covar_x_y=covar_x_y)
    q = Q_discrete_white_noise(dim=2, dt=dt, var=2)
    # TODO "For simplicity I will assume the noise is a discrete time Wiener process - that it is constant for each time
    # period. This assumption allows me to use a variance to specify how much I think the model changes between steps"
    # soooo change var?? idk. maybe should reflect the update_rate. Probably doesn't change much each 10Hz?
    kf.Q = block_diag(q, q)  # process noise x and y. TODO should probably change this to reflect the covariance i assume elsewhere
    #Q =[[0., var, 0., 0.]
    #   [var, var, 0., 0.]
    #   [0., 0., 0., var]
    #   [0., 0., var, var]]
    return kf


def calculate_distrust(quality):
    if quality == 0:
        quality = 0.01
    accuracy_UWB_localisation = 0.1  # m
    distrust = accuracy_UWB_localisation + 2 * (1000 / quality)
    # ex measurement: x = 5±0.1 if quality is 100, we want trust_in_measurement to be 1.1
    return distrust

# def init_kalman_filter_angle(loc_data, var_x=0.1, var_y=0.1, covar_x_y=0.2, dt=0.1):
#     kf = KalmanFilter(dim_x=4, dim_z=2)
#     #init state vector x:
#     kf.x = np.array([loc_data.x, loc_data.y, 0.0, 0.0])  # initialize with first loc_data x and y, 0 in velocity
#     kf.F = np.array([[1., 0., dt, 0],
#                     [0., 1., 0, dt],
#                     [0., 0., 1., 0.],
#                     [0., 0., 0., 1.]])
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


def measurement_noise_update(distrust_value, covar_x_y=0.2):
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
def kalman_updates(kf, loc_data):
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
    kf.predict()
    kf.update(z)
    filtered_loc = LocationData(x=kf.x[0], y=kf.x[1], z=0, quality=loc_quality)

    return filtered_loc  


def do_extended_kalman_filter(kalman_helper, x_state_vector):
    dim_x = 4  # state variables. tracking x,y,x_dot,y_dot = 4 state variables
    dim_z = 2  # measurement inputs. (x,y) = 2
    kf = ExtendedKalmanFilter(dim_x, dim_z)
    kf.x_state_vector == kalman_helper.state_vector





def get_state_vector(loc_as_dataframe):
    # want to return x_kf = [x y x_dot y_dot]

    np.array()
    return None
