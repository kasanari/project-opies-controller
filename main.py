from web_server import location_server
from websocket_server.websocket_server import create_websocket_task
from analysis.collect_data import fake_serial_task
from car.motor_control import motor_control_task
import argparse
import asyncio
import subprocess
from analysis.collect_data import collect_data_task
from serial_with_dwm.serial_manager import serial_man
from kalman.kalman_man import kalman_man
import csv
from websocket_server.websocket_server import ToWeb

PORT_NUMBER = 8080  # Port for web server


async def main_task_handler(ip_addr: str, serial_data_file: str = None, disable_motor: bool = False):
    message_queue: asyncio.Queue = asyncio.Queue()
    estimated_state_queue: asyncio.Queue = asyncio.Queue()
    measurement_queue: asyncio.Queue = asyncio.Queue()
    to_web_queue: asyncio.Queue[ToWeb] = asyncio.Queue()

    if serial_data_file is None:
        serial_man_task = asyncio.create_task(serial_man(measurement_queue, update_delay=0.3))
    else:
        serial_man_task = asyncio.create_task(fake_serial_task(serial_data_file, measurement_queue, update_delay=0.3))

    kalman_task = asyncio.create_task(kalman_man(measurement_queue, estimated_state_queue, to_web_queue=to_web_queue, dim_x=6, use_acc=True))

    motor_task = asyncio.create_task(motor_control_task(message_queue, measurement_queue, estimated_state_queue, debug_no_car=disable_motor))

    websocket_task = create_websocket_task(ip_addr, message_queue, to_web_queue)

    await asyncio.gather(serial_man_task, kalman_task, motor_task, websocket_task)


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
    parser.add_argument('ip_addr', metavar='IP', type=str, nargs='?',
                        help='The IP address to use.', default='localhost')
    parser.add_argument('--fake-serial', nargs='?', help='Use saved data instead of serial connection')
    parser.add_argument('--disable-motor', action='store_true', help='Do not use motor')
    parser.add_argument("-o", nargs='?', dest="out_file", help="output file name, in csv format. Defaults to a timestamp.")
    parser.add_argument("--no-saving", dest='no_saving', action='store_true', help="Disables saving results to a file")
    parser.add_argument("--collect-data", action="store_true")

    args = parser.parse_args()

    ip = args.ip_addr
    data_file = args.fake_serial
    disable_motor = args.disable_motor
    collect_data = args.collect_data


   # if not disable_motor:
        #kill_pigpiod()
        #subprocess.run("sudo pigpiod", shell=True, check=True)

    try:

        if not collect_data:
            location_server.start_web_client(PORT_NUMBER)
            asyncio.run(main_task_handler(ip, data_file, disable_motor=disable_motor))
        else:
            asyncio.run(collect_data_task(data_file, disable_motor=disable_motor, no_saving=args.no_saving, out_file=args.out_file))

    except KeyboardInterrupt:
        print("Stopping..")

    finally:
        #if not disable_motor:
            #kill_pigpiod()
        pass
