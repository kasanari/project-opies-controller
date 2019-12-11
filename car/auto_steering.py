from car.pidcontroller import PIDController
from arduino_interface import arduino_serial
from serial_with_dwm.location_data_handler import LocationData
import numpy as np
import asyncio
import pandas as pd
from asyncio import Queue
from dataclasses import dataclass

@dataclass
class Target:
    x: float
    y: float
    yaw: float

def position_error(target_x, target_y, x, y):
    y_diff = target_y - y
    x_diff = target_x - x
    return y_diff, x_diff


def angle_error(target_x, target_y, x, y):
    x_diff = target_x - x
    y_diff = target_y - y
    print(f"x_diff: {x_diff}")
    print(f"y_diff: {y_diff}")
    angle = (np.arctan2(y_diff, x_diff) - np.pi/2)*-1
    return np.rad2deg(angle)


def check_for_collision(connection, limit):
    distance = arduino_serial.measure_distance(connection)
    print(f"Distance in CM: {distance}")

    if distance < limit:
        return True

def approximate_angle(speed, wheel_angle, length = 2.45):
    return (speed * np.tan(wheel_angle)) / length


def approximate_speed(self, current_location: LocationData, current_time):
    return (self.prev_location.x - current_location.x) / (self.time - current_time)


def logger(self, **kwargs):
    # location = location.get_as_dict()
    time_stamp = pd.Timestamp.utcnow()
    self.data_log = self.data_log.append(pd.DataFrame(kwargs, index=[time_stamp]))

async def auto_steer_task(rc_car, destination, measurement_queue: Queue, estimated_state_queue: Queue, distance_control = False):

    target_x = destination['x']
    target_y = destination['y']

    print(f"Going to ({target_x}, {target_y})")
    loop = asyncio.get_running_loop()

    speed_controller = PIDController(K_p=0.2, K_d=0.02, K_i=0.00005)
    steering_controller = PIDController(K_p=45, K_d=30, K_i=0.1)
    
    if distance_control:
        arduino_connection = arduino_serial.connect_to_arduino()

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

            #e_angle = angle_error(target_x, target_y, location.x, location.y)
            y_diff, x_diff = position_error(target_x, target_y, loc_data.x, loc_data.y)

            if y_diff > 0:
                acceleration = 0.2
            else:
                await rc_car.brake()
                return

            #acceleration = speed_controller.get_control_signal(y_diff, loop.time(), P=True, D=True, I=False)
            angle = steering_controller.get_control_signal(x_diff, loop.time(), P=True, D=False) - 9.5

            print(f"acceleration: {acceleration}")
            print(f"angle: {angle}")

            rc_car.set_wheel_angle(angle)
            rc_car.set_acceleration(acceleration)
            print(f"---- {loop.time()} ----")

    except asyncio.CancelledError as e:
        print(e)
        rc_car.stop()
        print("Auto steer cancelled.")

    except Exception as e:
        print(e)

    finally:
        if distance_control:
            arduino_connection.close()