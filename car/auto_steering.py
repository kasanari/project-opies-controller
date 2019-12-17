import asyncio
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
from serial import Serial

from application import Context, Target
from arduino_interface import arduino_serial
from arduino_interface.imu import IMUData
from arduino_interface.ultrasonic import measure_distance
from car.pidcontroller import PIDController
from car.steering_control import SteeringController
from serial_with_dwm.location_data_handler import LocationData
import logging




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
                          target: Target,
                          distance_control=False):

    loc_data: LocationData
    imu_data: IMUData
    arduino_connection: Serial

    log = logging.getLogger('asyncio')
    log.debug("Going to (%d, %d) Angle: %d", target.x, target.y, target.yaw)

    speed_controller = PIDController(K_p=0.2, K_d=0.02, K_i=0.0002)

    steering_controller = SteeringController()

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
            measurements = context.measurement
            loc_data, imu_data = measurements
            log.info("Calculating control signal.")

            context.new_measurement_event.clear()
            context.new_estimated_state_event.clear()

            e_x, e_y, e_angle = calculate_lyapunov_errors(target, estimated_state.location_est, imu_data.rotation.yaw)
            speed = np.sqrt(np.square(estimated_state.x_v_est) + np.square(estimated_state.y_v_est))

            if e_y < 0:
                log.info("Done")
                context.auto_steering = False
                await rc_car.brake()
                return

            target_v_y = target.velocity
            e_v_y = target_v_y - estimated_state.y_v_est
            acceleration = 0.16#speed_controller.get_control_signal(e_v_y, time.time(), P=True, D=True, I=False)
            u_angle = steering_controller.get_control_signal(speed, e_angle, e_x,
                                                             time.time())  # steering_controller.get_control_signal(x_diff, loop.time(), P=True, D=False)

            acceleration = 0 if acceleration < 0 else acceleration


            log.debug(f"acceleration: {acceleration}")
            log.debug(f"u_angle: {u_angle}")

            context.control_signal.steering = u_angle
            context.control_signal.velocity = acceleration
            context.control_signal.target = target

            rc_car.set_wheel_angle(u_angle)
            rc_car.set_acceleration(acceleration)

            context.new_control_signal_event.set()


            #log.info("Auto Steering: Done for now.")

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
