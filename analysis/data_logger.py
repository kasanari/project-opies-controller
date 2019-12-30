import pandas as pd
import time

from arduino_interface.imu import IMUData
from application.context import ControlSignal
from kalman.EstimatedState import EstimatedState
from pathfinding.pathing import create_path_from_points, plot_pure_pursuit
from serial_with_dwm.location_data_handler import LocationData
from serial_with_dwm import Measurement
import matplotlib.pyplot as plt
import os


def fancy_scatter_plot(data, filename_timestamp):
    colors = data['quality']
    fig, ax = plt.subplots(1, 1)

    data.reset_index().plot.scatter(ax=ax, x='index', y=['x'], marker='o', c=colors, colormap='plasma')
    data.reset_index().plot.scatter(ax=ax, x='index', y=['y'], marker='o', c=colors, colormap='plasma')
    data.reset_index().plot.line(ax=ax, x='index', y=['x_kf', 'y_kf'])
    plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_fancy_line_plot.png"))
    fig.set_size_inches(15, 7, forward=True)


def generate_timestamp():
    timestamp = pd.Timestamp.utcnow().ctime()
    timestamp = str(timestamp).replace(" ", "_")
    timestamp = timestamp.replace(":", "")
    return timestamp


class DataLogger:

    def __init__(self):
        self.df = pd.DataFrame()
        self.start_time = time.time()
        self.filename_prefix = generate_timestamp()

    def plot_path(self, path_points, filename=None):

        fig, ax = plt.subplots(1, 1)
        ax.set_aspect('equal')
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 5)

        path = create_path_from_points(path_points["x"], path_points["y"])

        self.df.reset_index().plot.scatter(ax=ax, x='x_kf', y='y_kf')
        ax.scatter(path.x, path.y)

        if filename is None:
            plt.savefig(os.path.join(f'{self.filename_prefix}', f"{self.filename_prefix}_path.png"))
        else:
            plt.savefig(os.path.join(f"{filename}.png"))
        plt.show()

        plot_pure_pursuit(self.df.reset_index()["x"], self.df.reset_index()["y"], self.df.reset_index()["yaw"], path_points["x"], path_points["y"], filename=self.filename_prefix)

    def make_directory(self):
        os.mkdir(self.filename_prefix)

    def log_data(self, estimated_state: EstimatedState, control_signal: ControlSignal):
        imu_data: IMUData
        loc_data, imu_data = estimated_state.measurement.result_tag, estimated_state.measurement.result_imu

        if loc_data is None:
            loc_data = LocationData(0, 0, 0, 0)

        locations = {
            'x': loc_data.x,
            'y': loc_data.y,
            'target_y': control_signal.target.y,
            'target_x': control_signal.target.x,
            'quality': loc_data.quality,
            'x_kf': estimated_state.location_est.x,
            'y_kf': estimated_state.location_est.y,
            'y_dot': estimated_state.y_v_est,
            'x_dot': estimated_state.x_v_est,
            'a_x': imu_data.real_acceleration.x,
            'a_y': imu_data.real_acceleration.y,
            'a_x_kf': estimated_state.x_acc_est,
            'a_y_kf': estimated_state.y_acc_est,
            'yaw': imu_data.rotation.yaw,
            'u_v': control_signal.velocity,
            'u_yaw': control_signal.steering,
            'target_yaw': control_signal.target.yaw,
            'target_v': control_signal.target.velocity,
            'e_y': control_signal.error.y,
            'e_x': control_signal.error.x,
            'e_yaw': control_signal.error.yaw,
            'e_v': control_signal.error.velocity
        }

        time_stamp = (time.time() - self.start_time)
        self.df = self.df.append(pd.DataFrame(locations, index=[time_stamp]))

    def create_plots(self):
        # self.df.plot(x=['x', 'x_kf'], y=['y', 'y_kf'], kind='scatter')
        # plt.ylim(0, 5)
        # plt.xlim(0, 5)
        #
        filename_timestamp = self.filename_prefix
        #
        # plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_collect_data_scatter_plot.png"))

        # line plot
        self.df.reset_index().plot(x='index', y=['x', 'y', 'target_x', 'target_y', 'x_kf', 'y_kf'])

        plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_collect_data_line_plot_xy.png"))

        fancy_scatter_plot(self.df, filename_timestamp)

        # velocity
        self.df.reset_index().plot(x='index', y=['y_dot', 'x_dot'])
        plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_velocity.png"))

        # acceleration
        self.df.reset_index().plot(x='index', y=['a_y', 'a_x', 'a_x_kf', 'a_y_kf'])
        plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_acceleration.png"))


        # Steering control
        self.df.reset_index().plot(x='index', y=['u_yaw', 'target_yaw', 'yaw', 'e_yaw'])
        plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_steering_control.png"))


    def get_file_name(self, suffix, extension='png'):
        filename_timestamp = self.filename_prefix
        return f'{filename_timestamp}', f"{filename_timestamp}_{suffix}.{extension}"

    def save_csv(self):
        file_timestamp = self.filename_prefix
        self.df.to_csv(os.path.join(f'{file_timestamp}', f'{file_timestamp}.csv'), index_label='time')
