import re
import asyncio
import csv
import io
from dataclasses import dataclass


@dataclass
class Transform:
    x: float
    y: float
    z: float


@dataclass
class Rotation:
    yaw: float
    pitch: float
    roll: float


@dataclass
class IMUData:
    rotation: Rotation
    real_acceleration: Transform
    world_acceleration: Transform


async def start_IMU(connection):
    try:
        await asyncio.wait_for(calibrate_IMU(connection), timeout=10)
    except asyncio.TimeoutError:
        print("IMU setup timed out.")
        return False

    return True

async def calibrate_IMU(connection):
    match = None

    while (match is None):
        line = connection.readline().strip()
        line = line.decode()
        match = re.match("Send any character to begin DMP programming and demo:", line)
        await asyncio.sleep(0.1)

    connection.write(b'a\n')

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
    values = []

    while len(values) < 3:

        line = connection.readline().strip()
        line_str = line.decode()

        reader = csv.reader(
            io.StringIO(line_str),
            delimiter=',',
            quotechar='"',
            skipinitialspace=True,
        )

        try:
            values = next(reader)
        except StopIteration:
            values = []

    return values


def convert_g_to_acceleration(gs):
    for key in gs:
        gs[key] = (float(gs[key]) / 8192) * 9.82

    return gs


def read_IMU(connection):
    msg = "a\n".encode()
    connection.write(msg)

    ypr = read_csv_line(connection)
    realaccel = read_csv_line(connection)
    worldaccel = read_csv_line(connection)

    rotation = Rotation(float(ypr[0]), float(ypr[1]), float(ypr[2]))

    realaccel_dict = {"x": realaccel[0], "y": realaccel[1], "z": realaccel[2]}
    worldaccel_dict = {"x": worldaccel[0], "y": worldaccel[1], "z": worldaccel[2]}

    realaccel_dict = convert_g_to_acceleration(realaccel_dict)
    worldaccel_dict = convert_g_to_acceleration(worldaccel_dict)

    real_accel = Transform(realaccel_dict["x"], realaccel_dict["y"], realaccel_dict["z"])
    world_accel = Transform(worldaccel_dict["x"], worldaccel_dict["y"], worldaccel_dict["z"])

    return IMUData(rotation, real_accel, world_accel)
