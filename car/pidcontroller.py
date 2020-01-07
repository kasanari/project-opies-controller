import time


class PIDController:
    def __init__(self, p=1, d=1, i=1, enable_d=False, enable_i=False):
        self.prev_e = 0
        self.sum_e = 0
        self.K_p = p
        self.K_d = d
        self.K_i = i
        self.time = time.time()
        self.D = enable_d
        self.I = enable_i

    def get_constant_control_signal(self, error, current_time):

        e = error

        print(f"error: {e}")

        if e > 0:
            return 0.2
        elif e < 0:
            return -0.3
        else:
            return 0

    def get_control_signal(self, error, current_time):
        e = error
        control_signal = 0

        # print(f"error: {e}")

        delta_t = abs(current_time - self.time)
        self.time = current_time

        # print(f"delta_t = {delta_t}")
        p = self.K_p * e
        # print(f"p: {p}")
        control_signal += p
        if self.D:
            d = self.K_d * (e - self.prev_e) / delta_t
            control_signal += d
            self.prev_e = e
            # print(f"d: {d}")
        if self.I:
            i = self.K_i * self.sum_e
            control_signal += i
            self.sum_e += e * delta_t
            # print(f"i: {i}")




        return control_signal
