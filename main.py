from motor_control import motor_control_task
from web_server import location_server
from websocket_server import create_websocket_task
from serial_handler import serial_task
import argparse
import asyncio
import subprocess

PORT_NUMBER = 8080  # Port for web server


async def main_task_handler(ip_addr):
    message_queue = asyncio.Queue()
    location_queue = asyncio.Queue()
    location_task = asyncio.create_task(serial_task(location_queue))
    start_server = create_websocket_task(ip_addr, message_queue, location_queue)

    motor_task = asyncio.create_task(motor_control_task(message_queue))

    await asyncio.gather(start_server, motor_task, location_task)


def start_pigpiod():
    try:
        subprocess.run("sudo pigpiod", shell=True, check=True)
    except subprocess.CalledProcessError:
        pass


def kill_pigpiod():
    try:
        subprocess.run("sudo killall pigpiod", shell=True, check=True)
    except subprocess.CalledProcessError:
        pass


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start the car control server.')
    parser.add_argument('ip_addr', metavar='IP', type=str,
                        help='The IP address to use.')

    args = parser.parse_args()

    ip = args.ip_addr

    #kill_pigpiod()

    #subprocess.run("sudo pigpiod", shell=True, check=True)

    try:

        location_server.start_web_client(PORT_NUMBER)

        asyncio.run(main_task_handler(ip))

    except KeyboardInterrupt:
        print("Stopping..")

    finally:
        #kill_pigpiod()
        pass
