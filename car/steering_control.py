
class SteeringController:
    def __init__(self, K_1=1, K_2=0.9, K_3=2, K_4=0.5):
        self.prev_e = 0
        self.sum_e = 0
        self.K_1 = K_1
        self.K_2 = K_2
        self.K_3 = K_3
        self.K_4 = K_4
        self.time = time.time()


    def get_control_signal(self, speed, angle_error, lateral_error, current_time):

        control_signal = 0

        delta_t = abs(current_time - self.time)
        self.time = current_time

        control_signal += self.K_1 * angle_error

        try:
            control_signal += (self.K_2 * lateral_error)/speed
        except RuntimeWarning:
            pass

        control_signal += self.K_3 * (lateral_error - self.prev_e)/delta_t

        #control_signal += self.K_4 * self.sum_e

        self.sum_e += lateral_error*delta_t
        self.prev_e = lateral_error

        return control_signal