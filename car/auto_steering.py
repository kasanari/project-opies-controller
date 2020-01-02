import asyncio
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
from serial import Serial

from application.context import Target, Context
from arduino_interface import arduino_serial
from arduino_interface.imu import IMUData
from arduino_interface.ultrasonic import measure_distance
from car.pidcontroller import PIDController

from serial_with_dwm.location_data_handler import LocationData
from serial_with_dwm import Measurement
import pathfinding.pure_pursuit as pp
import pathfinding.pathing as pathing

import logging
import math


def position_error(target_x, target_y, x, y):
    y_diff = target_y - y
    x_diff = target_x - x
    return y_diff, x_diff


def angle_error(target_x, target_y, x, y):
    x_diff = target_x - x
    y_diff = target_y - y
    print(f"x_diff: {x_diff}")
    print(f"y_diff: {y_diff}")
    angle = (np.arctan2(y_diff, x_diff) - np.pi / 2) * -1
    return np.rad2deg(angle)


def check_for_collision(connection, limit):
    distance = measure_distance(connection)
    print(f"Distance in CM: {distance}")

    if distance < limit:
        return True


def logger(self, **kwargs):
    # location = location.get_as_dict()
    time_stamp = pd.Timestamp.utcnow()
    self.data_log = self.data_log.append(pd.DataFrame(kwargs, index=[time_stamp]))


def calculate_lyapunov_errors(target: Target, position: LocationData, angle):
    x_diff = target.x - position.x
    y_diff = target.y - position.y
    x = np.cos(angle) * x_diff + np.sin(angle) * y_diff
    y = -np.sin(angle) * x_diff + np.cos(angle) * y_diff
    theta = target.yaw - angle
    return x_diff, y_diff, theta


async def auto_steer_task(context: Context,
                          rc_car,
                          distance_control=False):

    loc_data: LocationData
    imu_data: IMUData
    arduino_connection: Serial

    log = logging.getLogger('asyncio')

    path_points = context.settings["path"]
    path = pathing.create_path_from_points(path_points["x"], path_points["y"])

    speed_controller = PIDController(K_p=1)

    if distance_control:
        arduino_connection: Serial = arduino_serial.connect_to_arduino()

    try:
        while True:

            if distance_control:
                collision_imminent = check_for_collision(arduino_connection, limit=60)
                if collision_imminent:
                    print("Stopping due to wall.")
                    await rc_car.brake()
                    rc_car.stop()
                    return


            log.info("Waiting for estimated state and measurements")
            await context.new_estimated_state_event.wait()
            estimated_state = context.estimated_state
            _, imu_data = estimated_state.measurement.result_tag, estimated_state.measurement.result_imu
            loc_data = estimated_state.location_est
            log.info("Calculating control signal.")

            context.new_estimated_state_event.clear()

            l = context.settings["lookahead"]

            tx, ty = pp.find_nearest_point(loc_data.x, loc_data.y, l, path)

            alpha, t_theta = pp.get_alpha(loc_data.x, loc_data.y, estimated_state.heading_est, tx, ty)

            u_angle = alpha #steering_controller.get_control_signal(alpha, time.time())  # steering_controller.get_control_signal(x_diff, loop.time(), P=True, D=False)

            speed = estimated_state.v_est
            target_speed = 0.5
            speed_error = target_speed - speed
            u_speed = 0.16 + speed_controller.get_control_signal(speed_error, time.time())
            if u_speed > 0.18:
                u_speed = 0.18
            elif u_speed < 0.16:
                u_speed = 0.16

            log.info(f"alpha: {alpha}")
            log.debug(f"acceleration: {u_speed}")
            log.debug(f"u_angle: {u_angle}")

            context.control_signal.steering = u_angle
            context.control_signal.velocity = u_speed
            context.control_signal.target = Target(tx, ty, yaw=t_theta)
            context.control_signal.error.yaw = alpha

            rc_car.set_wheel_angle(u_angle)
            rc_car.set_acceleration(u_speed)

            context.new_control_signal_event.set()


    except asyncio.CancelledError as e:
        print(e)
        await rc_car.brake()
        rc_car.stop()
        print("Auto steer cancelled.")

    except Exception as e:
        print(e)

    finally:
        if distance_control:
            arduino_connection.close()
