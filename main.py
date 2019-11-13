from motor_control import motor_control_task
from web_server import location_server
from websocket_server import create_websocket_task
import argparse
import asyncio
import subprocess

PORT_NUMBER = 8080  # Port for web server


async def main(ip_addr):
    queue = asyncio.Queue()

    start_server = create_websocket_task(ip_addr, queue)

    motor_task = asyncio.create_task(motor_control_task(queue))



    await asyncio.gather(start_server, motor_task)


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
        try:
            subprocess.run("sudo killall pigpiod", shell=True, check=True)
        except subprocess.CalledProcessError:
            pass
