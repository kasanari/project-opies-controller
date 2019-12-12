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
    matches = []
    retries = 0
    while len(matches) < 3 and retries < 10:

        line = connection.readline().strip()
        line_str = line.decode()

        matches = re.findall(r"(-?\d+\.?\d*)", line_str)

    values = [float(x) for x in matches]
    return values


def convert_g_to_acceleration(gs):
    for key in gs:
        gs[key] = (gs[key] / 4096) * 9.82 # IMU set to +- 8G resolution

    return gs


def read_IMU(connection):
    try:
        msg = "a\n".encode()
        connection.write(msg)

        ypr = read_csv_line(connection)
        realaccel = read_csv_line(connection)
        worldaccel = read_csv_line(connection)

        rotation = Rotation(ypr[0], ypr[1], ypr[2])

        realaccel_dict = {"x": realaccel[0], "y": realaccel[1], "z": realaccel[2]}
        worldaccel_dict = {"x": worldaccel[0], "y": worldaccel[1], "z": worldaccel[2]}

        realaccel_dict = convert_g_to_acceleration(realaccel_dict)
        worldaccel_dict = convert_g_to_acceleration(worldaccel_dict)

        real_accel = Transform(realaccel_dict["x"], realaccel_dict["y"], realaccel_dict["z"])
        world_accel = Transform(worldaccel_dict["x"], worldaccel_dict["y"], worldaccel_dict["z"])
        return IMUData(rotation, real_accel, world_accel)
    except RuntimeError as e:
        print(e)
        print("IMU read failed.")
        return None


