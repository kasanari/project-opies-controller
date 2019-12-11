import asyncio
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


async def motor_control_task(web_queue, measurement_queue, estimated_state_queue, control_signal_queue=None, debug_no_car=False):
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
                auto_steer = asyncio.create_task(auto_steer_task(rc_car,
                                                                 destination,
                                                                 measurement_queue,
                                                                 estimated_state_queue,
                                                                 control_signal_queue))

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
