import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import asyncio
import numpy as np
import csv
import argparse
from car.motor_control import motor_control_task
from kalman.kalman_filtering import init_kalman_filter, kalman_updates
from serial_with_dwm.serial_handler import serial_task
from serial_with_dwm.location_data_handler import LocationData
import datetime

matplotlib.use('Agg')
sleep_time = 20

def fancy_scatter_plot(data, filename_timestamp):
    colors = data['quality']
    fig, ax = plt.subplots(1, 1)

    data.reset_index().plot.scatter(ax=ax, x='index', y=['x'], marker='o', c=colors, colormap='plasma')
    data.reset_index().plot.scatter(ax=ax, x='index', y=['y'], marker='o', c=colors, colormap='plasma')
    data.reset_index().plot.line(ax=ax, x='index', y=['x_kf', 'y_kf'])
    plt.savefig(f"{filename_timestamp}_fancy_line_plot.png")
    fig.set_size_inches(15, 7, forward=True)
    plt.show()


def create_plots(dataframe, filename_timestamp):
    dataframe.plot(x=['x', 'x_kf'], y=['y', 'y_kf'], kind='scatter')
    plt.ylim(0, 5)
    plt.xlim(0, 5)
    plt.savefig(f"{filename_timestamp}_collect_data_scatter_plot.png")

    #Line plot
    dataframe.reset_index().plot(x='index', y=['x','y', 'target_x', 'target_y', 'x_kf', 'y_kf'])

    plt.savefig(f"{filename_timestamp}_collect_data_line_plot_xy.png")

    fancy_scatter_plot(dataframe, filename_timestamp)

async def fake_serial_task(data_file, *queues, update_delay=0.1):
    loc_data = lambda row: LocationData(float(row['x']), float(row['y']), 0, float(row['quality']))
    with open(data_file, newline='') as csvfile:
        rows = list(csv.DictReader(csvfile))
        kf = init_kalman_filter(loc_data(rows[0]), dt=update_delay, covar_x_y=0, dim_u=1)
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

async def log_task(location_queue):
    location_df = pd.DataFrame()
    start_time = datetime.datetime.now().timestamp()
    try:
        while True:
            location, location_filtered = await location_queue.get()

            locations = {
                'x': location.x,
                'y': location.y,
                'target_y': 2.5,
                'target_x': 1.8,
                'quality': location.quality,
                'x_kf': location_filtered.x,
                'y_kf': location_filtered.y
            }
            print(f"logging task: x is {location.x}")
            print(f"logging task: x_kf is {location_filtered.x}")
            print(f"quality is {location.quality}")
            time_stamp =  (datetime.datetime.now().timestamp() - start_time)
            location_df = location_df.append(pd.DataFrame(locations, index=[time_stamp]))

    except asyncio.CancelledError:
        print("Logging cancelled")
        return location_df


async def collect_data_task(data_file=None, disable_motor=True, no_saving=False, out_file=None) :
    message_queue = asyncio.Queue()
    serial_queue = asyncio.Queue()
    log_queue = asyncio.Queue()
    motor_task = None
    fake_serial = False

    if data_file is None:
        location_task = asyncio.create_task(serial_task(log_queue, serial_queue)) # use real serial
    else:
        location_task = asyncio.create_task(fake_serial_task(data_file, log_queue, serial_queue)) #get data from file
        fake_serial = True

    if not disable_motor:
        message = {'type': "destination", 'x': 0.8, 'y': 10}
        await message_queue.put(message)
        motor_task = asyncio.create_task(motor_control_task(message_queue, serial_queue))

    logging_task = asyncio.create_task(log_task(log_queue))

    await asyncio.sleep(sleep_time)
    location_task.cancel()

    if not disable_motor and motor_task is not None:
        motor_task.cancel()

    logging_task.cancel()
    result : pd.DataFrame = await logging_task

    file_timestamp = generate_timestamp()

    if fake_serial:
        file_timestamp += "_fake"

    if not no_saving:
        if out_file is None:
            result.to_csv(f'{file_timestamp}.csv')
        else:
            result.to_csv(out_file)

    create_plots(result, file_timestamp)

    print("Done")


def generate_timestamp():
    timestamp = pd.Timestamp.utcnow().ctime()
    timestamp = str(timestamp).replace(" ", "_")
    timestamp = timestamp.replace(":", "")
    return timestamp
