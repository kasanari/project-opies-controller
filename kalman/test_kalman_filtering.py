import pandas as pd
import numpy as np
from analysis.data_logger import DataLogger
from application.context import Context, ControlSignal
from arduino_interface.imu import IMUData, Rotation, Transform
from kalman.PositionEstimator import PositionEstimator
from serial_with_dwm import LocationData, Measurement

df = pd.read_csv("/Users/Torun/Teknisk fysik/OPIES/project-opies-controller/analysis/data/Sun_Jan__5_093226_2020.csv")


data_logger = DataLogger()
context = Context("/Users/Torun/Teknisk fysik/OPIES/project-opies-controller/application/default_settings.json")
position_estimator = PositionEstimator(**context.settings["kalman"])
start = True
for x, y, u_yaw, yaw, a_r_y, a_r_x, a_w_y, a_w_x in zip(df["x"], df["y"], df["u_yaw"], df["yaw_kf"],
                                                                 df["a_r_y"], df["a_r_x"], df["a_w_y"],
                                                                 df["a_w_x"]):

    if yaw < 0:
        yaw += 360
    tan_u = np.tan(u_yaw)

    loc_data = LocationData(x, y, 1.5, 100)
    rotation = Rotation(yaw, 0, 0)
    real_acc = Transform(a_r_x, a_r_y, 0)
    world_acc = Transform(a_w_x, a_w_y, 0)
    imu_data = IMUData(rotation=rotation, real_acceleration=real_acc, world_acceleration=world_acc)
    measurement = Measurement(loc_data, imu_data)
    control_signal = ControlSignal(0, tan_u)
    if start:
        position_estimator.start_kalman_filter(loc_data)
        start=False
        continue

    estimated_state = position_estimator.do_kalman_updates(loc_data,
                                                            imu_data,
                                                            control_signal = control_signal.to_numpy())
    estimated_state.measurement = measurement
    data_logger.log_data(estimated_state, control_signal)

data_logger.make_directory()
data_logger.save_csv()
data_logger.create_plots()