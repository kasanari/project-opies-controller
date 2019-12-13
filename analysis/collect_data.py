from asyncio import Queue

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import asyncio
import numpy as np
import csv
import os
import argparse

from arduino_interface.imu import IMUData
from car.auto_steering import Target, ControlSignal
from car.motor_control import motor_control_task
from kalman.kalman_filtering import init_kalman_filter, kalman_updates, EstimatedState
from kalman.kalman_man import kalman_man
from serial_with_dwm.location_data_handler import LocationData
import time

from serial_with_dwm.serial_manager import serial_man

matplotlib.use('Agg')

def fancy_scatter_plot(data, filename_timestamp):
    colors = data['quality']
    fig, ax = plt.subplots(1, 1)

    data.reset_index().plot.scatter(ax=ax, x='index', y=['x'], marker='o', c=colors, colormap='plasma')
    data.reset_index().plot.scatter(ax=ax, x='index', y=['y'], marker='o', c=colors, colormap='plasma')
    data.reset_index().plot.line(ax=ax, x='index', y=['x_kf', 'y_kf'])
    plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_fancy_line_plot.png"))
    fig.set_size_inches(15, 7, forward=True)
    plt.show()


def create_plots(dataframe, filename_timestamp):
    dataframe.plot(x=['x', 'x_kf'], y=['y', 'y_kf'], kind='scatter')
    plt.ylim(0, 5)
    plt.xlim(0, 5)
    plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_collect_data_scatter_plot.png"))

    # line plot
    dataframe.reset_index().plot(x='index', y=['x', 'y', 'target_x', 'target_y', 'x_kf', 'y_kf'])

    plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_collect_data_line_plot_xy.png"))

    fancy_scatter_plot(dataframe, filename_timestamp)

    # velocity
    dataframe.reset_index().plot(x='index', y=['y_dot', 'x_dot'])
    plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_velocity.png"))

    # yaw
    dataframe.reset_index().plot(x='index', y='yaw')
    plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_yaw.png"))

    # acceleration
    dataframe.reset_index().plot(x='index', y=['a_y', 'a_x', 'a_x_kf', 'a_y_kf'])
    plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_acceleration.png"))

    # Control
    dataframe.reset_index().plot(x='index', y=['u_v', 'target_v', 'y_dot'])
    plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_velocity_control.png"))

    dataframe.reset_index().plot(x='index', y=['u_yaw', 'target_yaw', 'yaw'])
    plt.savefig(os.path.join(f'{filename_timestamp}', f"{filename_timestamp}_steering_control.png"))

async def fake_serial_task(data_file, *queues, update_delay=0.1):
    loc_data = lambda row: LocationData(float(row['x']), float(row['y']), 0, float(row['quality']))
    with open(data_file, newline='') as csvfile:
        rows = list(csv.DictReader(csvfile))
        kf = init_kalman_filter(loc_data(rows[0]), dt=update_delay, dim_u=1)
        while True:
            for row in rows:
                location_data = loc_data(row)
                steering_signal = np.array([1])  # temp
                loc_data_filtered = kalman_updates(kf, loc_data(row), update_delay, u=steering_signal)
                tasks = [q.put([location_data, loc_data_filtered]) for q in queues]
                await asyncio.gather(*tasks)
                await asyncio.sleep(update_delay)
            for row in reversed(rows):
                location_data = loc_data(row)
                steering_signal = np.array([0.2])  # temp
                loc_data_filtered = kalman_updates(kf, loc_data(row), update_delay, u=steering_signal)
                tasks = [q.put([location_data, loc_data_filtered]) for q in queues]
                await asyncio.gather(*tasks)
                await asyncio.sleep(update_delay)

async def log_task(measurement_queue,
                   estimated_state_queue: Queue,
                   control_signal_queue: Queue,
                   target: Target):
    location_df = pd.DataFrame()
    start_time = time.time()
    imu_data: IMUData
    try:
        while True:
            estimated_state: EstimatedState = await estimated_state_queue.get()
            measurements = await measurement_queue.get()
            #control_signal: ControlSignal = await control_signal_queue.get()
            control_signal = ControlSignal(0, 0)
            loc_data, imu_data = measurements

            if loc_data is None:
                loc_data = LocationData(0, 0, 0, 0)

            locations = {
                'x': loc_data.x,
                'y': loc_data.y,
                'target_y': target.y,
                'target_x': target.x,
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
                'target_yaw': target.yaw,
                'target_v': target.velocity
            }
            #print(f"logging task: x is {loc_data.x}")
            #print(f"logging task: x_kf is {estimated_state.location_est.x}")
            #print(f"quality is {loc_data.quality}")
            time_stamp = (time.time() - start_time)
            location_df = location_df.append(pd.DataFrame(locations, index=[time_stamp]))

    except asyncio.CancelledError:
        print("Logging cancelled")
        return location_df


async def collect_data_task(data_file=None, disable_motor=True, no_saving=False, out_file=None, sleep_time=10):
    message_queue = asyncio.Queue()
    measurement_queue = asyncio.Queue()
    estimated_state_queue = asyncio.Queue()
    control_queue = asyncio.Queue()
    motor_task = None
    fake_serial = False

    control_queue.put_nowait(ControlSignal(0, 0))

    if data_file is None:
        location_task = asyncio.create_task(serial_man(measurement_queue)) # use real serial
    else:
        location_task = asyncio.create_task(fake_serial_task(data_file, measurement_queue)) #get data from file
        fake_serial = True

    kalman_task = asyncio.create_task(kalman_man(measurement_queue, estimated_state_queue, control_queue=control_queue, dim_u=2, use_acc=True))

    target = Target(0.8, 7, 0, 2.5)

    if not disable_motor:
        message = {'type': "destination", 'x': target.x, 'y': target.y, "yaw": target.yaw, "speed": target.velocity}
        await message_queue.put(message)
        motor_task = asyncio.create_task(motor_control_task(message_queue,
                                                            measurement_queue,
                                                            estimated_state_queue,
                                                            control_signal_queue=control_queue))

    logging_task = asyncio.create_task(log_task(measurement_queue, estimated_state_queue, control_queue, target))

    await asyncio.sleep(sleep_time)
    location_task.cancel()
    kalman_task.cancel()

    if not disable_motor and motor_task is not None:
        motor_task.cancel()

    logging_task.cancel()
    result: pd.DataFrame = await logging_task

    file_timestamp = generate_timestamp()

    os.mkdir(file_timestamp)

    if fake_serial:
        file_timestamp += "_fake"

    if not no_saving:
        if out_file is None:
            result.to_csv(os.path.join(f'{file_timestamp}', f'{file_timestamp}.csv'), index_label='time')
        else:
            result.to_csv(out_file, index_label='time')

    create_plots(result, file_timestamp)

    print("Done")


def generate_timestamp():
    timestamp = pd.Timestamp.utcnow().ctime()
    timestamp = str(timestamp).replace(" ", "_")
    timestamp = timestamp.replace(":", "")
    return timestamp
