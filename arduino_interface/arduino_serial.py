import serial
import time
import json
import asyncio
import csv
import io
import re


async def calibrate_IMU(connection):
    match = None

    while (match is None):
        line = connection.readline().strip()
        line = line.decode()
        match = re.match("Send any character to begin DMP programming and demo:", line)
        await asyncio.sleep(0.1)

    connection.write(b'a\n')

    await asyncio.sleep(5)

    match = None

    while (match is None):
        line = connection.readline().strip()
        line = line.decode()
        match = re.match("DMP ready! Waiting for first interrupt...", line)
        await asyncio.sleep(0.1)

    connection.flushInput()
    print("IMU startup complete.")
    return

def read_csv_line(connection):
    line = connection.readline().strip()
    line = line.replace(b'\x00', b'')
    line_str = line.decode()

    reader = csv.reader(
        io.StringIO(line_str),
        delimiter=',',
        quotechar='"',
        skipinitialspace=True,
    )

    return next(reader)

def convert_g_to_acceleration(gs):

    for key in gs:
        gs[key] = (float(gs[key])/8192) * 9.82

    return gs

def read_IMU(connection):
    msg = "a\n".encode()
    connection.write(msg)

    ypr = read_csv_line(connection)
    realaccel = read_csv_line(connection)
    worldaccel = read_csv_line(connection)

    ypr_dict = {"yaw":float(ypr[0]), "pitch":float(ypr[1]), "roll":float(ypr[2])}
    realaccel_dict = {"x":realaccel[0], "y":realaccel[1], "z":realaccel[2]}
    worldaccel_dict = {"x":worldaccel[0], "y":worldaccel[1], "z":worldaccel[2]}

    realaccel_dict = convert_g_to_acceleration(realaccel_dict)
    worldaccel_dict = convert_g_to_acceleration(worldaccel_dict)

    print(ypr_dict)
    print(realaccel_dict)
    print(worldaccel_dict)




def connect_to_arduino():
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2)
    except serial.SerialException:
        ser = serial.Serial('/dev/ttyUSB2', 115200, timeout=2)

    return ser


def measure_distance(connection):
    line = b''

    while line == b'':
        msg = "a\n".encode()
        connection.write(msg)
        line = connection.readline()

    return int(line)


async def main(connection):
    calibrate = asyncio.create_task(calibrate_IMU(connection))

    await asyncio.sleep(10)

    if not calibrate.done():
     calibrate.cancel()

    while 1:
        read_IMU(connection)
        print("--------")


if __name__ == "__main__":

    a_ser = None

    try:

        a_ser = connect_to_arduino()

        asyncio.run(main(a_ser))

    except KeyboardInterrupt:
        print("Stopping")
        if a_ser is not None:
            a_ser.close()
