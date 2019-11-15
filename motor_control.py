import asyncio
from car import Car
from location_data_handler import LocationData


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


async def motor_control_task(web_queue, from_serial_queue: asyncio.Queue):

    rc_car = Car()

    sign = lambda x: -1 if x < 0 else (1 if x > 0 else (0 if x == 0 else None))

    print("Waiting for speed controller...")

    await asyncio.sleep(2)

    print("Initialized motors.")

    try:
        while True:
            message = await web_queue.get()
            message_type = message["type"]

            #if message_type == "car_control":
            #    control_car_from_message(rc_car, message)

            #elif message_type == "destination":
            #    print(f"Going to ({message['x']}, {message['y']})")

            if message_type == 'stop':
                rc_car.stop()
                return
            else:

                x_destination = message["x"]
                y_destination = message["y"]
                prev_y_diff = 1
                rc_car.steering_servo.value = -0.15
                while True:
                    location: LocationData = await from_serial_queue.get()
                    try:
                        x_diff = int(x_destination) - location.x
                    except ValueError:
                        x_diff = 0
                    try:
                        y_diff = int(y_destination) - location.y
                    except ValueError:
                        y_diff = 0
                    print(f"deltaX: {x_diff}, deltaY: {y_diff}")

                    if sign(y_diff) != sign(prev_y_diff):
                        print("sign change!")
                        rc_car.motor_servo.value = 0
                        await asyncio.sleep(10)

                    if y_diff > 0:
                        rc_car.motor_servo.value = 0.2
                    elif y_diff < 0:
                        rc_car.motor_servo.value = -0.3
                    else:
                        rc_car.motor_servo.value = 0

                    prev_y_diff = y_diff

    except asyncio.CancelledError:
        print("Motor task cancelled.")
    finally:
       rc_car.disable()
