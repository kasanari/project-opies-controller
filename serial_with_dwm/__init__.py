from dataclasses import dataclass
from serial_with_dwm.location_data_handler import LocationData
from arduino_interface.imu import IMUData


@dataclass
class Measurement:
    result_tag: LocationData
    result_imu: IMUData