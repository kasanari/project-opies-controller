from kalman.nonlinear_kalman_filtering import init_unscented_kf, u_kalman_updates, init_extended_kf, e_kalman_updates
import time

class PositionEstimator:

    def __init__(self, std_dev_acc=0.8, std_dev_position=0.2, std_dev_heading=0.8, update_delay=0.1,
                 std_dev_angular_acc=0.2):
        self.std_dev_acc = std_dev_acc
        self.std_dev_angular_acc = std_dev_angular_acc
        self.std_dev_position = std_dev_position
        self.std_dev_heading = std_dev_heading
        self.update_delay = update_delay
        self.kf = None
        self.estimated_state = None
        #self.time = time.time()

    def start_kalman_filter(self, loc_data):
        self.kf = init_extended_kf(loc_data, dt=self.update_delay, variance_acc=self.std_dev_acc,
                                    variance_pos=self.std_dev_position, variance_heading=self.std_dev_heading,
                                    variance_angular_acc=self.std_dev_angular_acc)

    def do_kalman_updates(self, loc_data, imu_data):
        self.estimated_state = e_kalman_updates(self.kf, loc_data, imu_data, variance_position=self.std_dev_position,
                                                variance_acceleration=self.std_dev_acc,
                                                variance_heading=self.std_dev_heading)  #
        #self.time = time.time()
        return self.estimated_state

    # TODO fundera på tidsstegen här. vi kollar tiden det tar att läsa location, används den?

    def get_settings_as_dict(self):
        dict = {
            'std_dev_acc': self.std_dev_acc,
            'std_dev_position': self.std_dev_position,
            #'std_dev_velocity': self.std_dev_velocity,
        }

        return dict


