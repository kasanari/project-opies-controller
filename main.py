from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from web_server import location_server
import argparse
import json
import asyncio
import random
import datetime
import functools
import subprocess
from websockets import WebSocketServerProtocol, ConnectionClosedError

PORT_NUMBER = 8080  # Port for web server

async def time():  # TODO change this to send location info as well as time
    """Generates a message containing the location of the Pi and the current time"""
    await asyncio.sleep(1)  # To simulate a delay in getting the location data
    data_to_send = {
        'x': random.randint(0, 10),
        'y': random.randint(0, 10),
        'timestamp': datetime.datetime.utcnow().isoformat()
    }

    return json.dumps(data_to_send)


async def send_handler(websocket, path):
    """ Sends location data (only time currently) to client """
    print("Client Connected!")
    while True:
        message = await time()
        await websocket.send(message)


async def receive_handler(websocket, path, queue):
    """ Handles incoming messages from client """
    try:
        async for message in websocket:
            await queue.put(message)
    except ConnectionClosedError:
        return


async def handler(websocket: WebSocketServerProtocol, path: str, queue):
    """ Starts all tasks related to websockets and motor control"""
    receive_msg_task = asyncio.create_task(receive_handler(websocket, path, queue))
    send_msg_task = asyncio.create_task(send_handler(websocket, path))

    done, pending = await asyncio.wait([receive_msg_task, send_msg_task], return_when=asyncio.FIRST_COMPLETED)
    print("Client Disconnected!")
    for task in pending:
        task.cancel()


async def motor_control_task(queue):
    factory = PiGPIOFactory()

    motor_max_duty = 0.1
    motor_min_duty = 0.05
    min_pulse_width = motor_min_duty * 20/1000
    max_pulse_width = motor_max_duty * 20/1000
    steering = Servo(13, pin_factory=factory)
    motor = Servo(19, pin_factory=factory, min_pulse_width=min_pulse_width, max_pulse_width=max_pulse_width)

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
            elif message_type == 'stop':
                motor.mid()
                steering.mid()

    except asyncio.CancelledError:
        print("Motor task cancelled.")
    finally:
        steering.detach()
        motor.detach()


async def main(ip_addr):
    queue = asyncio.Queue()

    start_server = location_server.start_websocket_server(ip_addr, functools.partial(handler, queue=queue))

    motor_task = asyncio.create_task(motor_control_task(queue))

    await asyncio.gather(start_server, motor_task)

    # asyncio.get_event_loop().run_until_complete(start_server)
    # asyncio.get_event_loop().run_forever()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start the car control server.')
    parser.add_argument('ip_addr', metavar='IP', type=str,
                        help='The IP address to use.')

    args = parser.parse_args()

    ip = args.ip_addr

    try:
        subprocess.run("sudo killall pigpiod", shell=True, check=True)
    except subprocess.CalledProcessError:
        pass

    subprocess.run("sudo pigpiod", shell=True, check=True)

    try:

        location_server.start_web_client(PORT_NUMBER)

        asyncio.run(main(ip))

    except KeyboardInterrupt:
        print("Stopping..")
        #asyncio.get_event_loop().stop()
        try:
            subprocess.run("sudo killall pigpiod", shell=True, check=True)
        except subprocess.CalledProcessError:
            pass
