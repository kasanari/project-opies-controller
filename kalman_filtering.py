from filterpy.kalman import ExtendedKalmanFilter
import numpy as np


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


def do_kalman_filter(kalman_helper, x_state_vector):
    dim_x = 4  # state variables. tracking x,y,x_dot,y_dot = 4 state variables
    dim_z = 2  # measurement inputs. (x,y) = 2
    kf = ExtendedKalmanFilter(dim_x, dim_z)
    kf.x_state_vector == kalman_helper.state_vector





def get_state_vector(loc_as_dataframe):
    # want to return x_kf = [x y x_dot y_dot]

    np.array()
    return None
