import location_server
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import json
import asyncio
import random
import datetime
from websockets import WebSocketServerProtocol


async def time():  # TODO change this to send location info as well as time
    await asyncio.sleep(1)
    data_to_send = {
        'x': random.randint(0, 10),
        'y': random.randint(0, 10),
        'timestamp': datetime.datetime.utcnow().isoformat()
    }

    return json.dumps(data_to_send)


async def time_handler(websocket, path):
    print("Client Connected!")
    while True:
        message = await time()
        await websocket.send(message)


async def order_handler(websocket, path, queue):
    async for message in websocket:
        await queue.put(message)


async def handler(websocket: WebSocketServerProtocol, path: str):
    queue = asyncio.Queue()
    consumer_task = asyncio.create_task(order_handler(websocket, path, queue))
    producer_task = asyncio.create_task(time_handler(websocket, path))
    motor_task = asyncio.create_task(motor_control_task(queue))

    done, pending = await asyncio.wait([consumer_task, producer_task, motor_task], return_when=asyncio.FIRST_COMPLETED)
    print("Client Disconnected!")
    for task in pending:
        task.cancel()


async def motor_control_task(queue):
    factory = PiGPIOFactory()
    steering = Servo(13, pin_factory=factory)
    motor = Servo(19, pin_factory=factory)

    print("Initialized motors.")

    try:
        while True:
            message = await queue.get()
            message = json.loads(message)
            print(message)

            message_type = message["type"]

            if message_type == "car_control":
                try:
                    angle = float(message["angle"])
                    steering.value = angle
                except ValueError as e:
                    print(e)

                try:
                    speed = float(message["speed"])
                    motor.value = speed
                except ValueError as e:
                    print(e)
            elif message_type == "destination":
                print(f"Going to ({message['x']}, {message['y']})")

    except asyncio.CancelledError:
        print("Motor task cancelled.")
    finally:
        steering.detach()
        motor.detach()


if __name__ == "__main__":

    try:
        location_server.start_web_client()
        start_server = location_server.start_websocket_server(handler)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    except KeyboardInterrupt:
        print("Stopping..")
        asyncio.get_event_loop().stop()
        #cleanup()