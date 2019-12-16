import asyncio
import csv

import numpy as np

from application import Context, Target
from car.car import Car
from car.motor_control import motor_control_task
from kalman.kalman_filtering import init_kalman_filter, kalman_updates
from kalman.kalman_man import kalman_man
from serial_with_dwm.location_data_handler import LocationData
from serial_with_dwm.serial_manager import serial_man


async def fake_serial_task(context, data_file, update_delay=0.1):
    loc_data = lambda row: LocationData(float(row['x']), float(row['y']), 0, float(row['quality']))
    with open(data_file, newline='') as csvfile:
        rows = list(csv.DictReader(csvfile))
        kf = init_kalman_filter(loc_data(rows[0]), dt=update_delay, dim_u=1)
        while True:
            for row in rows:
                steering_signal = np.array([1])  # temp
                estimated_state = kalman_updates(kf, loc_data(row), update_delay, u=steering_signal, timestep=0.1)
                context.estimated_state = estimated_state
                context.new_estimated_state_event.set()
                await asyncio.sleep(update_delay)
            for row in reversed(rows):
                steering_signal = np.array([0.2])  # temp
                context.estimated_state = kalman_updates(kf, loc_data(row), update_delay, u=steering_signal, timestep=0.1)
                context.new_estimated_state_event.set()
                await asyncio.sleep(update_delay)


async def collect_data_task(data_file=None, disable_motor=True, no_saving=False, out_file=None, sleep_time=10):

    message_task = None

    context = Context()

    try:
        rc_car = Car(disable_motor)
    except OSError as e:
        print(e)
        print("Failed to connect to PIGPIOD")
        return

    if data_file is None:
        location_task = asyncio.create_task(serial_man(context)) # use real serial
    else:
        location_task = asyncio.create_task(fake_serial_task(context, data_file)) #get data from file

    kalman_task = asyncio.create_task(kalman_man(context, dim_u=2, use_acc=True))

    target = Target(0.8, 7, 0, 2.5)

    if not disable_motor:
        message = {'type': "destination", 'x': target.x, 'y': target.y, "yaw": target.yaw, "speed": target.velocity}
        await context.from_web_queue.put(message)
        message_task = asyncio.create_task(motor_control_task(context, rc_car))

    await asyncio.sleep(sleep_time)
    kalman_task.cancel()
    location_task.cancel()

    if not disable_motor and message_task is not None:
        message_task.cancel()

    print("Done")



