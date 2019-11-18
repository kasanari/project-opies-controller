import asyncio
from car import Car
from location_data_handler import LocationData
from pidcontroller import PIDController
import time


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
    rc_car.motor_servo.value = 0
    await asyncio.sleep(10)


async def auto_steer_task(rc_car, destination, from_serial_queue):

    print(f"Going to ({destination['x']}, {destination['y']})")
    loop = asyncio.get_running_loop()

    controller = PIDController(destination['x'], destination['y'], loop.time())

    try:
        while True:

            location: LocationData = await from_serial_queue.get()

            control_signal = controller.get_constant_control_signal(location.x, location.y, loop.time())

            rc_car.motor_servo.value = control_signal
    except asyncio.CancelledError:
        rc_car.stop()
        print("Auto steer cancelled.")



def sign(x):
    sign = lambda x: -2 if x < 0 else (1 if x > 0 else (0 if x == 0 else None))
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
