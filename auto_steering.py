from location_data_handler import LocationData, Transform
from pidcontroller import PIDController
from arduino_interface import arduino_serial
from steering_controller import SteeringController
import numpy as np
import pandas as pd
import asyncio


def approximate_angle(length, speed, wheel_angle):
    return (speed * np.tan(wheel_angle)) / length


async def check_for_collision(limit):
    distance = await arduino_serial.distance_measure()
    print(f"Distance in CM: {distance}")

    if distance < limit:
        return True


class AutoPilot:

    def __init__(self, target: LocationData, angle):
        self.target = target
        self.data_log = pd.DataFrame()
        self.prev_location = Transform(0, 0, 0)
        self.target_angle = angle
        self.time = 0

    def calculate_errors(self, position: LocationData, angle):
        x_diff = self.target.x - position.x
        y_diff = self.target.y - position.y
        x = np.cos(angle) * x_diff + np.sin(angle) * y_diff
        y = -np.sin(angle) * x_diff + np.cos(angle) * y_diff
        theta = self.target_angle - angle
        return x, y, theta

    def position_error(self, x, y):
        y_diff = self.target.y - y
        return y_diff

    def angle_error(self, x, y):
        x_diff = self.target.x - x
        y_diff = self.target.y - y
        print(f"x_diff: {x_diff}")
        print(f"y_diff: {y_diff}")
        angle = (np.arctan2(y_diff, x_diff) - np.pi / 2) * -1
        return np.rad2deg(angle)

    async def auto_steer_task(self, rc_car, from_serial_queue, distance_control: bool =False):

        print(f"Going to ({self.target.x}, {self.target.y})")
        loop = asyncio.get_running_loop()

        speed_controller = PIDController(K_p=0.2, K_d=0.02, K_i=0.00005)
        steering_controller = SteeringController()
        wheel_angle = 0

        try:
            while True:

                if distance_control:
                    collision_imminent = await check_for_collision(limit=40)
                    if collision_imminent:
                        print("Stopping due to wall.")
                        rc_car.brake()
                        rc_car.stop()
                        return

                location: LocationData = await from_serial_queue.get()

                speed = self.approximate_speed(location, loop.time())
                heading_angle = approximate_angle(2.65, speed, wheel_angle)

                print(f"speed: {speed}")
                print(f"heading_angle: {heading_angle}")

                x_e, y_e, angle_e = self.calculate_errors(location, heading_angle)

                print(f"x_e: {x_e}")
                print(f"y_e: {y_e}")
                print(f"angle_e: {angle_e}")

                acceleration = speed_controller.get_control_signal(y_e, loop.time(), P=True, D=True, I=False)
                wheel_angle = steering_controller.get_control_signal(speed, angle_e, x_e, loop.time())

                print(f"acceleration: {acceleration}")
                print(f"wheel_angle: {wheel_angle}")

                rc_car.set_wheel_angle(wheel_angle)
                rc_car.set_acceleration(acceleration)

                #self.logger(y_loc=location.y, error=e_pos)
                self.prev_location = Transform(location.x, location.y, 0)

                print(f"---- {loop.time()} ----")

        except asyncio.CancelledError as e:
            print(e)
            rc_car.stop()
            print("Auto steer cancelled.")

        except Exception as e:
            print(e)
            rc_car.stop()
            return

    def logger(self, **kwargs):
        # location = location.get_as_dict()
        time_stamp = pd.Timestamp.utcnow()
        self.data_log = self.data_log.append(pd.DataFrame(kwargs, index=[time_stamp]))

    def approximate_speed(self, current_location: LocationData, current_time):
        return (self.prev_location.x - current_location.x) / (self.time - current_time)
