from arduino_interface.imu import IMUData
from car.pidcontroller import PIDController
from arduino_interface import arduino_serial
from car.steering_control import SteeringController
from kalman.kalman_filtering import EstimatedState
from serial_with_dwm.location_data_handler import LocationData
import numpy as np
import asyncio
import pandas as pd
from asyncio import Queue
from car.car import Car
from dataclasses import dataclass
from serial import Serial
import time


@dataclass
class Target:
    x: float
    y: float
    yaw: float

@dataclass
class ControlSignal:
    velocity: float
    steering: float


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
    distance = arduino_serial.measure_distance(connection)
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


async def auto_steer_task(rc_car,
                          destination,
                          measurement_queue: Queue,
                          estimated_state_queue: Queue,
                          control_signal_queue: Queue = None,
                          distance_control=False):

    target: Target = Target(destination['x'], destination['y'], 0)
    loc_data: LocationData
    imu_data: IMUData
    arduino_connection: Serial

    print(f"Going to ({target.x}, {target.y}) Angle: {target.yaw}")

    speed_controller = PIDController(K_p=0.2, K_d=0.05, K_i=0.0002)
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

            measurements = await measurement_queue.get()  # location = location_filtered
            await measurement_queue.put(measurements)
            loc_data, imu_data = measurements
            estimated_state: EstimatedState = await estimated_state_queue.get()
            await estimated_state_queue.put(estimated_state)

            # e_angle = angle_error(target_x, target_y, location.x, location.y)
            # y_diff, x_diff = position_error(target_x, target_y, loc_data.x, loc_data.y)

            e_x, e_y, e_angle = calculate_lyapunov_errors(target, estimated_state.location_est, imu_data.rotation.yaw)
            speed = np.sqrt(np.square(estimated_state.x_v_est) + np.square(estimated_state.y_v_est))

            if e_y < 0:
                print("Done")
                await rc_car.brake()
                return

            target_v_y = 2
            e_v_y = target_v_y - estimated_state.y_v_est
            acceleration = speed_controller.get_control_signal(e_v_y, time.time(), P=True, D=True, I=True)
            u_angle = steering_controller.get_control_signal(speed, e_angle, e_x,
                                                             time.time())  # steering_controller.get_control_signal(x_diff, loop.time(), P=True, D=False)

            print(f"acceleration: {acceleration}")
            print(f"u_angle: {u_angle}")

            rc_car.set_wheel_angle(u_angle)
            rc_car.set_acceleration(acceleration)
            print(f"---- {time.time()} ----")
            await asyncio.sleep(0.05)

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
