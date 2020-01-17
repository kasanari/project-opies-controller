import asyncio
import logging
import os
from application.context import Context
from car.auto_steering import auto_steer_task
from car.car import Car


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
        logging.getLogger('asyncio').error("Failed to connect to PIGPIOD")
        return

    logging.getLogger('asyncio').info("Waiting for speed controller...")

    await asyncio.sleep(2)
    logging.getLogger('asyncio').info("Initialized motors.")

    auto_steer = None

    try:
        while True:
            message = await context.from_web_queue.get()
            message_type = message["type"]

            if message_type == "car_control":
                if auto_steer is not None:
                    auto_steer.cancel()
                control_car_from_message(rc_car, message)

            elif message_type == "destination" or message_type == "path":
                context.settings["path"]["x"] = [float(x) for x in message["x"]]
                context.settings["path"]["y"] = [float(y) for y in message["y"]]

                try:
                    filename = message["filename"]  # To prevent hackers
                    filename = "movie"
                    movie_path = os.path.join(os.getcwd(),'web_server', 'static',  filename)

                    if os.path.isfile(f"{movie_path}.mp4"):
                        os.remove(f"{movie_path}.mp4")

                except KeyError:
                    movie_path = None


                if auto_steer is not None:
                    rc_car.stop()
                    auto_steer.cancel()

                auto_steer = asyncio.create_task(auto_steer_task(context, rc_car, movie_filename=movie_path))
                context.auto_steering = True

            elif message_type == 'stop':
                if auto_steer is not None:
                    auto_steer.cancel()
                else:
                    await rc_car.brake()

            elif message_type == 'brake':
                await rc_car.brake()

            else:
                logging.getLogger('asyncio').warning("Invalid message type")

    except asyncio.CancelledError:
        rc_car.stop()
        logging.getLogger('asyncio').info("Motor task cancelled.")
    finally:
        #await rc_car.brake()
        rc_car.disable()
