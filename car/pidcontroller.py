import time

class PIDController:
    def __init__(self, K_p=1, K_d=1, K_i=1):
        self.prev_e = 0
        self.sum_e = 0
        self.K_p = K_p
        self.K_d = K_d
        self.K_i = K_i
        self.time = time.time()

    def get_constant_control_signal(self, error, current_time):

        e = error

        print(f"error: {e}")

        if e > 0:
            return 0.2
        elif e < 0:
            return -0.3
        else:
            return 0

    def get_control_signal(self, error, current_time, P=True, D=False, I=False):
        e = error
        control_signal = 0

        print(f"error: {e}")

        delta_t = abs(current_time - self.time)
        self.time = current_time

        print(f"delta_t = {delta_t}")

        if P:
            p = self.K_p * e
            print(f"p: {p}")
            control_signal += p
        if D:
            d = self.K_d * (e - self.prev_e)/delta_t
            control_signal += d
            print(f"d: {d}")
        if I:
            i = self.K_i * self.sum_e
            control_signal += i
            print(f"i: {i}")

        self.sum_e += e*delta_t
        self.prev_e = e

        return control_signal
