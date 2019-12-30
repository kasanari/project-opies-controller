import asyncio

from application.context import Target, Context
from car.car import Car
from car.auto_steering import auto_steer_task


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


async def motor_control_task(context: Context, debug_no_car=False):
    try:
        rc_car = Car(debug_no_car)
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
            message = await context.from_web_queue.get()
            message_type = message["type"]

            if message_type == "car_control":
                if auto_steer is not None:
                    auto_steer.cancel()
                control_car_from_message(rc_car, message)

            elif message_type == "destination":
                x_destination = message["x"]
                y_destination = message["y"]

                try:
                    yaw = message["yaw"]
                except KeyError:
                    yaw = 0

                try:
                    speed = message["speed"]
                except KeyError:
                    speed = 2

                if auto_steer is not None:
                    auto_steer.cancel()

                context.auto_steering = True
                target = Target(x_destination, y_destination, yaw, speed)
                auto_steer = asyncio.create_task(auto_steer_task(context, rc_car, target))

            elif message_type == 'stop':
                if auto_steer is not None:
                    auto_steer.cancel()
                else:
                    await rc_car.brake()

            elif message_type == 'brake':
                await rc_car.brake()

            else:
                print("Invalid message type")

    except asyncio.CancelledError:
        print("Motor task cancelled.")
    finally:
        await rc_car.brake()
        rc_car.disable()
