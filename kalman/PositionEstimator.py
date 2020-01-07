from kalman.kalman_filtering import init_kalman_filter, kalman_updates
import time

class PositionEstimator:

    def __init__(self, process_dev_pos, process_dev_acc, process_dev_heading, process_dev_heading_acc,
                 process_dev_vel,
                 meas_dev_pos, meas_dev_heading, meas_dev_acc, speed_div_by_length, dim_z = 5, dim_u=0,
                 dim_x=6, update_delay=0.1):
        self.process_var_acc = process_dev_acc
        self.process_var_vel = process_dev_vel
        self.process_var_heading = process_dev_heading
        self.process_var_heading_acc = process_dev_heading_acc
        self.process_var_pos = process_dev_pos
        self.meas_var_pos = meas_dev_pos
        self.meas_var_heading = meas_dev_heading
        self.meas_var_acc = meas_dev_acc
        self.dim_u = dim_u
        self.dim_x = dim_x
        self.dim_z = dim_z
        self.update_delay = update_delay
        self.kf = None
        self.estimated_state = None
        self.time = time.time()
        self.speed_div_by_length = speed_div_by_length

    def start_kalman_filter(self, loc_data):
        self.kf = init_kalman_filter(loc_data, process_var_pos=self.process_var_pos, process_var_acc=self.process_var_acc,
                                     process_var_heading=self.process_var_heading,
                                     process_var_heading_acc=self.process_var_heading_acc,
                                     process_var_vel=self.process_var_vel, dt=self.update_delay, dim_x=self.dim_x, dim_z=self.dim_z, dim_u=self.dim_u, use_acc=True,
                                     speed_div_by_length=self.speed_div_by_length,
                                     meas_var_acc=self.meas_var_acc, meas_var_heading=self.meas_var_heading, meas_var_pos=self.meas_var_pos
                                     )

    def do_kalman_updates(self, loc_data, imu_data, control_signal, variable_dt=True):
        if variable_dt:
            d_t = time.time() - self.time
        else:
            d_t = self.update_delay

        self.estimated_state = kalman_updates(self.kf, loc_data, imu_data, variance_position=self.meas_var_pos,
                                              variance_acceleration=self.meas_var_acc,
                                              variance_heading=self.meas_var_heading,
                                              process_var_pos=self.process_var_pos,
                                              process_var_heading=self.process_var_heading,
                                              process_var_heading_acc=self.process_var_heading_acc,
                                              process_var_acc=self.process_var_acc,
                                              process_var_velocity=self.process_var_vel,
                                              u=control_signal,
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


