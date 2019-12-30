from dataclasses import dataclass

from serial_with_dwm import LocationData, Measurement


@dataclass
class EstimatedState:
    location_est: LocationData
    #x_v_est: float
    #y_v_est: float
    v_est: float
    log_likelihood: float
    likelihood: float
    a_est: float
    heading_est: float
    #x_acc_est: float
    #y_acc_est: float
    measurement: Measurement = None