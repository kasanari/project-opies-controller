import location_server
from motor_control import Steering, Motor, cleanup
import json
import asyncio
import random
import datetime
from websockets import WebSocketServerProtocol

PORT_NUMBER = 8080  # Port for web server
IP = "192.168.1.251"  # IP for websocket server


# IP = "192.168.0.24"

async def time():  # TODO change this to send location info as well as time
    """Generates a message containing the location of the Pi and the current time"""
    await asyncio.sleep(1)  # To simulate a delay in getting the location data
    data_to_send = {
        'x': random.randint(0, 10),
        'y': random.randint(0, 10),
        'timestamp': datetime.datetime.utcnow().isoformat()
    }

    return json.dumps(data_to_send)


async def time_handler(websocket, path):
    """ Sends location data (only time currently) to client """
    print("Client Connected!")
    while True:
        message = await time()
        await websocket.send(message)


async def order_handler(websocket, path, queue):
    """ Handles incoming messages from client """
    async for message in websocket:
        await queue.put(message)


async def handler(websocket: WebSocketServerProtocol, path: str):
    """ Starts all tasks related to websockets and motor control"""
    queue = asyncio.Queue()
    consumer_task = asyncio.create_task(order_handler(websocket, path, queue))
    producer_task = asyncio.create_task(time_handler(websocket, path))
    motor_task = asyncio.create_task(motor_control_task(queue))

    done, pending = await asyncio.wait([consumer_task, producer_task, motor_task], return_when=asyncio.FIRST_COMPLETED)
    print("Client Disconnected!")
    for task in pending:
        task.cancel()


async def motor_control_task(queue):
    """ Controls the steering servo and motor, awaits orders from queue"""
    steering = Steering(17, 4, 13)
    motor = Motor(18)

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
                    steering.set_angle(angle)
                except ValueError as e:
                    print(e)

                try:
                    speed = float(message["speed"])
                    motor.set_speed(speed)
                except ValueError as e:
                    print(e)
            elif message_type == "destination":
                print(f"Going to ({message['x']}, {message['y']})")

    except asyncio.CancelledError:
        print("Motor task cancelled.")
    finally:
        steering.stop()
        motor.stop()


if __name__ == "__main__":

    try:
        location_server.start_web_client(PORT_NUMBER)
        start_server = location_server.start_websocket_server(IP, handler)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    except KeyboardInterrupt:
        print("Stopping..")
        asyncio.get_event_loop().stop()
        cleanup()
