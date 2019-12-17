from kalman.kalman_filtering import init_kalman_filter, kalman_updates
import time

class PositionEstimator:

    def __init__(self, std_dev_acc=0.8, std_dev_position=0.2, std_dev_velocity=0.8, dim_u=0,
                 dim_x=6, update_delay=0.1):
        self.std_dev_acc = std_dev_acc
        self.std_dev_position = std_dev_position
        self.std_dev_velocity = std_dev_velocity
        self.dim_u = dim_u
        self.dim_x = dim_x
        self.update_delay = update_delay
        self.kf = None
        self.estimated_state = None
        self.time = time.time()

    def start_kalman_filter(self, loc_data):
        self.kf = init_kalman_filter(loc_data, dt=self.update_delay, dim_x=self.dim_x, dim_u=self.dim_u, use_acc=True,
                                     variance_acc=self.std_dev_acc, variance_position=self.std_dev_position,
                                     variance_velocity=self.std_dev_velocity)

    def do_kalman_updates(self, loc_data, imu_data, control_signal, variable_dt=False):
        if variable_dt:
            d_t = time.time() - self.time
        else:
            d_t = self.update_delay

        self.estimated_state = kalman_updates(self.kf, loc_data, imu_data, variance_position=self.std_dev_position,
                                              variance_acceleration=self.std_dev_acc, u=control_signal,
                                              timestep=d_t, use_acc=True)
        self.time = time.time()
        return self.estimated_state

    # TODO fundera på tidsstegen här. vi kollar tiden det tar att läsa location, används den?

    def get_settings_as_dict(self):
        dict = {
            'std_dev_acc': self.std_dev_acc,
            'std_dev_position': self.std_dev_position,
            'std_dev_velocity': self.std_dev_velocity,
        }

        return dict


