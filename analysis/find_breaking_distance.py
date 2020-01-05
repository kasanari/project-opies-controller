import asyncio
import csv

import matplotlib.pyplot as plt
import pandas as pd

from car.motor_control import motor_control_task
from serial_with_dwm.location_data_handler import LocationData

sleep_time = 3


def create_plots(dataframe, timestamp, brake_time_stamp):
    dataframe.plot(x=['x', 'x_kf'], y=['y', 'y_kf'], kind='scatter')
    plt.ylim(0, 5)
    plt.xlim(0, 5)
    plt.savefig(f"{timestamp}_scatter_plot.png")
    fig, ax = plt.subplots(1, 1)

    # Line plot
    dataframe.reset_index().plot(ax=ax, x='index', y=['x', 'y', 'target_x', 'target_y', 'x_kf', 'y_kf'])
    plt.axvline(brake_time_stamp)

    plt.savefig(f"{timestamp}_line_plot.png")


async def start_and_brake(reverse=True):
    message_queue = asyncio.Queue()
    serial_queue = asyncio.Queue()
    log_queue = asyncio.Queue()
    print("Starting..")

    go_forward_message = {
        'type': 'car_control',
        'angle': -9.5,
        'speed': 0.2
    }
    location_task = asyncio.create_task(serial_task(log_queue, serial_queue))  # use real serial

    await message_queue.put(go_forward_message)
    motor_task = asyncio.create_task(motor_control_task(message_queue, serial_queue))
    timestamp = generate_timestamp(pd)
    logging_task = asyncio.create_task(log_task(log_queue, file_timestamp=timestamp, asyncio=asyncio, pd=pd))
    await asyncio.sleep(7)

    go_forward_message = {
        'type': 'brake',
    }

    await message_queue.put(go_forward_message)
    brake_time_stamp = pd.Timestamp.utcnow()

    await asyncio.sleep(6)

    message2 = {
        'type': 'car_control',
        'angle': -9.5,
        'speed': -0.2
    }
    if reverse:
        await message_queue.put(message2)
        await asyncio.sleep(2)
        await message_queue.put(go_forward_message)

    location_task.cancel()

    motor_task.cancel()
    logging_task.cancel()

    result: pd.DataFrame = await logging_task

    timestamp = generate_timestamp()
    result.to_csv(f'{timestamp}.csv')

    create_plots(result, timestamp, brake_time_stamp)

    print("Done")


async def start_and_stop_and_start():
    message_queue = asyncio.Queue()
    serial_queue = asyncio.Queue()
    log_queue = asyncio.Queue()
    print("Starting..")

    brake_message = {
        'type': 'car_control',
        'angle': -9.5,
        'speed': 0.2
    }
    location_task = asyncio.create_task(serial_task(log_queue, serial_queue))  # use real serial

    await message_queue.put(brake_message)
    motor_task = asyncio.create_task(motor_control_task(message_queue, serial_queue))
    logging_task = asyncio.create_task(log_task(log_queue))
    await asyncio.sleep(sleep_time)

    brake_message = {
        'type': 'brake',
    }

    await message_queue.put(brake_message)
    brake_time_stamp = pd.Timestamp.utcnow()

    message2 = {
        'type': 'car_control',
        'angle': -9.5,
        'speed': 0.2
    }
    print("Starting again.")
    await message_queue.put(message2)
    await asyncio.sleep(2)

    print("Should brake here")
    await message_queue.put(brake_message)

    print("Quitting")
    location_task.cancel()

    motor_task.cancel()
    logging_task.cancel()

    result: pd.DataFrame = await logging_task

    timestamp = generate_timestamp(pd)
    result.to_csv(f'{timestamp}.csv')

    create_plots(result, brake_time_stamp)

    print("Done")


async def log_task(location_queue, file_timestamp, asyncio, pd, target_y=2.5, target_x=1.8):
    location_df = pd.DataFrame()
    try:
        while True:
            location, location_filtered = await location_queue.get()

            locations = {
                'x': location.x,
                'y': location.y,
                'target_y': target_y,
                'target_x': target_x,
                'quality': location.quality,
                'x_kf': location_filtered.x,
                'y_kf': location_filtered.y
            }

            time_stamp = pd.Timestamp.utcnow()
            # time_stamp = generate_timestamp(pd)
            location_df = location_df.append(pd.DataFrame(locations, index=[time_stamp]))

    except asyncio.CancelledError:
        print("Logging cancelled")
        return location_df


async def fake_serial_task(data_file, asyncio, *queues):
    with open(data_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            location_data = LocationData(float(row['x']), float(row['y']), float(row['z']), float(row['quality']))
            tasks = [q.put(location_data) for q in queues]
            await asyncio.gather(*tasks)


def generate_timestamp(pd):
    timestamp = pd.Timestamp.utcnow().ctime()
    timestamp = str(timestamp).replace(" ", "_")
    timestamp = timestamp.replace(":", "")
    return timestamp


if __name__ == "__main__":
    asyncio.run(start_and_brake())
