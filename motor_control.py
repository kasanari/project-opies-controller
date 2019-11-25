import asyncio
from car import Car
from location_data_handler import LocationData
from pidcontroller import PIDController
from arduino_interface import arduino_serial
import numpy as np


def control_car_from_message(rc_car, message):
    try:
        angle = float(message["angle"])
        rc_car.set_wheel_angle(angle)
    except ValueError as e:
        print(e)

    try:
        speed = float(message["speed"])
        rc_car.set_acceleration(speed)
    except ValueError as e:
        print(e)


def position_error(target_x, target_y, x, y):
    y_diff = target_y - y
    return y_diff


def angle_error(target_x, target_y, x, y):
    x_diff = target_x - x
    y_diff = target_y - y
    print(f"x_diff: {x_diff}")
    print(f"y_diff: {y_diff}")
    angle = (np.arctan2(y_diff, x_diff) - np.pi/2)*-1
    return np.rad2deg(angle)

def check_for_collision(limit):
    distance = await arduino_serial.distance_measure()
    print(f"Distance in CM: {distance}")

    if distance < limit:
        return True


async def auto_steer_task(rc_car, destination, from_serial_queue, distance_control = True):

    target_x = destination['x']
    target_y = destination['y']

    print(f"Going to ({target_x}, {target_y})")
    loop = asyncio.get_running_loop()

    speed_controller = PIDController(K_p=0.2, K_d=0.02, K_i=0.00005)
    steering_controller = PIDController(K_p=0.2, K_d=0.02, K_i=0.00005)

    try:
        while True:

            if distance_control:
                collision_imminent = check_for_collision(limit=40)
                if (collision_imminent):
                    print("Stopping due to wall.")
                    rc_car.brake()
                    rc_car.stop()
                    return


            location: LocationData = await from_serial_queue.get()

            e_angle = angle_error(target_x, target_y, location.x, location.y)
            e_pos = position_error(target_x, target_y, location.x, location.y)

            acceleration = speed_controller.get_control_signal(e_pos, loop.time(), P=True, D=True, I=False)
            angle = steering_controller.get_control_signal(e_angle, loop.time())

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


async def motor_control_task(web_queue, from_serial_queue):

    try:
        rc_car = Car()
    except OSError as e:
        print(e)
        print("Failed to connect to PIGPIOD")
        return

    print("Waiting for speed controller...")

    await asyncio.sleep(2)

    print("Initialized motors.")

    auto_steer = None

    try:
        while True:
            message = await web_queue.get()
            message_type = message["type"]

            if message_type == "car_control":
                if auto_steer is not None:
                    auto_steer.cancel()
                control_car_from_message(rc_car, message)

            elif message_type == "destination":
                x_destination = message["x"]
                y_destination = message["y"]
                destination = {'x': float(x_destination), 'y': float(y_destination)}
                if auto_steer is not None:
                    auto_steer.cancel()
                auto_steer = asyncio.create_task(auto_steer_task(rc_car, destination, from_serial_queue))

            elif message_type == 'stop':
                if auto_steer is not None:
                    auto_steer.cancel()
                else:
                    rc_car.stop()
            else:
                print("Invalid message type")


    except asyncio.CancelledError:
        print("Motor task cancelled.")
    finally:
       rc_car.disable()
