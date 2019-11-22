import asyncio
from car import Car
from location_data_handler import LocationData
from pidcontroller import PIDController
from arduino_interface import arduino_serial
import time
import numpy as np


def control_car_from_message(rc_car, message):
    try:
        angle = float(message["angle"])
        rc_car.steering_servo.value = angle
    except ValueError as e:
        print(e)

    try:
        speed = float(message["speed"])
        rc_car.motor_servo.value = speed
    except ValueError as e:
        print(e)


async def reverse(rc_car):
    print("Setting brake")
    rc_car.motor_servo.value = -0.2
    await asyncio.sleep(1.5)
    print("waiting...")
    rc_car.motor_servo.value = 0
    await asyncio.sleep(1.5)


def position_error(self, x, y):
    y_diff = self.target_y - y
    return y_diff


def angle_error(self, x, y):
    x_diff = self.target_x - x
    y_diff = self.target_y - y
    print(f"x_diff: {x_diff}")
    print(f"y_diff: {y_diff}")
    angle = (np.arctan2(y_diff, x_diff) - np.pi/2)*-1
    return angle


async def auto_steer_task(rc_car, destination, from_serial_queue, distance_control = True):

    print(f"Going to ({destination['x']}, {destination['y']})")
    loop = asyncio.get_running_loop()

    controller = PIDController(destination['x'], destination['y'], 0, K_p=0.2, K_d=0.06, K_i=0.00005)

    prev_control_signal = None



    rc_car.steering_servo.value = -0.2

    try:
        while True:

            if distance_control:
                distance = await arduino_serial.distance_measure()
                print(f"Distance in CM: {distance}")

                if distance < 40:
                    print("Too close!")
                    rc_car.motor_servo.value = -0.15
                    await asyncio.sleep(1)
                    rc_car.stop()
                    return

            location: LocationData = await from_serial_queue.get()

            control_signal = controller.get_control_signal(location.x, location.y, loop.time(), P=True, D=True, I=False)

            angle = angle_error(controller, location.x, location.y)

            print(f"control_signal: {control_signal}")
            print(f"angle: {np.rad2deg(angle)}")

            if control_signal > 0.2:
                control_signal = 0.2

            elif control_signal < 0.1:
                control_signal = -0.4
            #elif control_signal < -0.4:
            #    control_signal = -0.4

            if prev_control_signal is not None:
                if (prev_control_signal > 0) and control_signal < 0:
                    print("Reverse")

                    #await reverse(rc_car)

            rc_car.motor_servo.value = control_signal
            prev_control_signal = control_signal
            print("----")

    except asyncio.CancelledError:
        rc_car.stop()
        print("Auto steer cancelled.")



def sign(x):
    sign = lambda x: -1 if x < 0 else (1 if x > 0 else (0 if x == 0 else None))
    return sign(x)

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
