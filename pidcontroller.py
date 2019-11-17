class PIDController:
    def __init__(self, target_x, target_y, current_time, K_p=1, K_d=1, K_i=1):
        self.target_x = target_x
        self.target_y = target_y
        self.prev_e = 0
        self.sum_e = 0
        self.K_p = K_p
        self.K_d = K_d
        self.K_i = K_i
        self.time = current_time

    def get_constant_control_signal(self, x, y, current_time):

        e = self.error(x, y)

        print(f"error: {e}")

        if e > 0:
            return 0.2
        elif e < 0:
            return -0.3
        else:
            return 0

    def get_control_signal(self, x, y, current_time, P=True, D=False, I=False):
        e = self.error(x, y)
        control_signal = 0

        delta_t = abs(current_time - self.time)
        self.time = current_time

        if P:
            control_signal = self.K_p * e
        if D:
            control_signal += self.K_d * (e - self.prev_e)/delta_t
        if I:
            control_signal += self.K_i * self.sum_e

        self.sum_e += e*delta_t
        return control_signal


    def error(self, x, y):
        x_diff = x - self.target_x
        return x_diff

