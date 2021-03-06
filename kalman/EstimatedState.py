from dataclasses import dataclass

from serial_with_dwm import LocationData, Measurement


@dataclass
class EstimatedState:
    location_est: LocationData
    x_v_est: float
    y_v_est: float
    log_likelihood: float
    likelihood: float
    x_acc_est: float
    y_acc_est: float
    yaw_est: float
    yaw_acc_est: float
    measurement: Measurement = None  # has result_tag, result_imu