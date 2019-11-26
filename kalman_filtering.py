from filterpy.kalman import KalmanFilter, ExtendedKalmanFilter
from filterpy.common import Q_discrete_white_noise
import numpy as np
from scipy.linalg import block_diag
from location_data_handler import LocationData


class KalmanHelper:

    def __init__(self, loc_data):
        self.x_vector = np.array(loc_data.x)
        self.x_dot = np.array([0])
        self.y_vector = np.array(loc_data.y)
        self.y_dot = np.array([0])
        self.state_vector = np.array(self.x_vector, self.y_vector, self.x_dot, self.y_dot)  # state vector. in KF
        # theory, called x

    def update_loc_vectors(self, loc_data):
        self.x_vector = np.append(self.x_vector, loc_data.x)
        self.y_vector = np.append(self.y_vector, loc_data.y)

    def update_velocities(self, past_loc, current_loc, delta):
        new_x_dot = (current_loc.x-past_loc.x)/delta
        new_y_dot = (current_loc.y-past_loc.y)/delta
        self.x_dot = np.append(self.x_dot, new_x_dot)
        self.y_dot = np.append(self.y_dot, new_y_dot)

    def update_state_vector(self):
        self.state_vector = np.array(self.x_vector, self.y_vector, self.x_dot, self.y_dot)


# var_x and var_y in meters
def init_kalman_filter(loc_data, var_x=0.1, var_y=0.1, covar_x_y=0.2, dt=0.1):
    kf = KalmanFilter(dim_x=4, dim_z=2)  
    #init state vector x:
    kf.x = np.array([loc_data.x, loc_data.y, 0.0, 0.0])  # initialize with first loc_data x and y, 0 in velocity
    kf.F = np.array([[1.,0., dt, 0],
                    [0.,1., 0, dt],
                    [0., 0., 1., 0.],
                    [0., 0., 0., 1.]])
    kf.H = np.array([[1.,0., 0., 0.],
                    [0., 1., 0., 0.]])
    kf.P *= loc_data.quality # P is a unit matrix. Multiply it with quality factor of first measurement. Maybe higher value?
      # measurement noise. not sure what values to put here.
    kf.R = measurement_noise_update(loc_data, var_x=var_x, var_y=var_y, covar_x_y=covar_x_y)
    q = Q_discrete_white_noise(dim=2, dt=dt, var=0.001)
    kf.Q = block_diag(q, q)  # process noise x and y
    #Q =[[0., var, 0., 0.]
    #   [var, var, 0., 0.]
    #   [0., 0., 0., var]
    #   [0., 0., var, var]]
    return kf

def init_kalman_filter_angle(loc_data, var_x=0.1, var_y=0.1, covar_x_y=0.2, dt=0.1):
    kf = KalmanFilter(dim_x=4, dim_z=2)  
    #init state vector x:
    kf.x = np.array([loc_data.x, loc_data.y, 0.0, 0.0])  # initialize with first loc_data x and y, 0 in velocity
    kf.F = np.array([[1.,0., dt, 0],
                    [0.,1., 0, dt],
                    [0., 0., 1., 0.],
                    [0., 0., 0., 1.]])
    kf.H = np.array([[1.,0., 0., 0.],
                    [0., 1., 0., 0.]])
    kf.P *= loc_data.quality # P is a unit matrix. Multiply it with quality factor of first measurement. Maybe higher value?
      # measurement noise. not sure what values to put here.
    kf.R = measurement_noise_update(loc_data, var_x=var_x, var_y=var_y, covar_x_y=covar_x_y)
    q = Q_discrete_white_noise(dim=2, dt=dt, var=0.001)
    kf.Q = block_diag(q, q)  # process noise x and y
    #Q =[[0., var, 0., 0.]
    #   [var, var, 0., 0.]
    #   [0., 0., 0., var]
    #   [0., 0., var, var]]
    return kf

def measurement_update(loc_data):
    z = [[loc_data.x],
        [loc_data.y]]
    return z

def measurement_noise_update(loc_data, var_x=0.1, var_y=0.1, covar_x_y=0.2):
    var_x = var_x/loc_data.quality
    var_y = var_y/loc_data.quality
    r = np.array([[var_x, covar_x_y],
                  [covar_x_y, var_y]])
    return r


def kalman_updates(kf, loc_data):
    if loc_data is None:
        loc_data = LocationData(x=0, y=0, quality=0.00000000000000000000000001)
    z = measurement_update(loc_data)
    kf.R = measurement_noise_update(loc_data)
    kf.predict()
    kf.update(z)
    filtered_loc = LocationData(x=kf.x[0], y=kf.x[1], z=0, quality=-1)

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
