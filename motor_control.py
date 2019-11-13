import asyncio
from car import Car


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


async def motor_control_task(queue):

    rc_car = Car()

    print("Initialized motors.")

    try:
        while True:
            message = await queue.get()
            message_type = message["type"]

            if message_type == "car_control":
                control_car_from_message(rc_car, message)

            elif message_type == "destination":
                print(f"Going to ({message['x']}, {message['y']})")

            elif message_type == 'stop':
                rc_car.stop()

    except asyncio.CancelledError:
        print("Motor task cancelled.")
    finally:
       rc_car.disable()
