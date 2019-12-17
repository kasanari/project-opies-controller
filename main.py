import argparse
import asyncio
import subprocess

from analysis.collect_data import collect_data_task
from analysis.collect_data import fake_serial_task
from application import Context
from car.motor_control import motor_control_task
from kalman.kalman_man import kalman_man
from serial_with_dwm.serial_manager import serial_man
from web_server import location_server
from websocket_server.websocket_server import create_websocket_task

PORT_NUMBER = 8080  # Port for web server


async def main_task_handler(ip_addr: str, serial_data_file: str = None, disable_motor: bool = False):

    context = Context()

    if serial_data_file is None:
        serial_man_task = asyncio.create_task(serial_man(context, update_delay=0.3))
    else:
        serial_man_task = asyncio.create_task(fake_serial_task(context, serial_data_file, update_delay=0.3))

    kalman_task = asyncio.create_task(kalman_man(context))

    motor_task = asyncio.create_task(motor_control_task(context, debug_no_car=disable_motor))

    websocket_task = create_websocket_task(context, ip_addr)

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

def start_collect_data(args):
    args = vars(args)
    del args["func"]
    asyncio.run(
        collect_data_task(**args)
    )

def start_gui(args):
    args = vars(args)
    del args["func"]
    location_server.start_web_client(PORT_NUMBER)
    asyncio.run(main_task_handler(**args))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Start the car control server.')
    parser.add_argument('--fake-serial', nargs='?', dest='serial_data_file', help='Use saved data instead of serial connection')
    parser.add_argument('--disable-motor', action='store_true', help='Do not use motor')

    subparsers = parser.add_subparsers(help='subcommands help')

    gui_parser = subparsers.add_parser("gui", help='Start the car control server.')
    gui_parser.add_argument('ip_addr', metavar='IP', type=str, nargs='?',
                 help='The IP address to use.', default='localhost')
    gui_parser.set_defaults(func=start_gui)

    collect_data_parser = subparsers.add_parser("collect-data", help="automatically run the car and log data")
    collect_data_parser.add_argument("--sleep-time", nargs='?', dest='sleep_time', type=int)
    collect_data_parser.add_argument("-o", nargs='?', dest="out_file", help="output file name, in csv format. Defaults to a timestamp.")
    collect_data_parser.add_argument("--no-saving", dest='no_saving', action='store_true', help="Disables saving results to a file")
    collect_data_parser.set_defaults(func=start_collect_data)

    args = parser.parse_args()
    args.func(args)
