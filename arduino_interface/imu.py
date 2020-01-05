import asyncio
import re
from dataclasses import dataclass
import logging

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
        logging.getLogger('asyncio').error("IMU setup timed out.")
        return False

    return True


async def calibrate_IMU(connection):
    match = None

    while match is None:
        line = connection.readline().strip()
        line = line.decode()
        match = re.match("Send any character to begin DMP programming and demo:", line)
        await asyncio.sleep(0.1)

    connection.write(b'a\n')

    match = None

    while match is None:
        line = connection.readline().strip()
        line = line.decode()
        match = re.match("DMP ready! Waiting for first interrupt...", line)
        await asyncio.sleep(0.1)

    connection.flushInput()
    logging.getLogger('asyncio').info("IMU startup complete.")
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
        gs[key] = (gs[key] / 4096) * 9.82  # IMU set to +- 8G resolution

    return gs


def read_IMU(connection):
    try:
        msg = "a\n".encode()
        connection.write(msg)

        ypr = read_csv_line(connection)
        realaccel = read_csv_line(connection)
        worldaccel = read_csv_line(connection)

        rotation = Rotation(ypr[0], ypr[1], ypr[2])

        rotation.yaw *= -1
        if rotation.yaw < 0:
            rotation.yaw += 360

        #flips imu x and y
        realaccel_dict = {"x": realaccel[0], "y": realaccel[1], "z": realaccel[2]}
        worldaccel_dict = {"x": worldaccel[0], "y": worldaccel[1], "z": worldaccel[2]}

        realaccel_dict = convert_g_to_acceleration(realaccel_dict)
        worldaccel_dict = convert_g_to_acceleration(worldaccel_dict)

        for key in realaccel_dict:
            realaccel_dict[key] = float_with_2_decimals(realaccel_dict[key])

        for key in worldaccel_dict:
            worldaccel_dict[key] = float_with_2_decimals(worldaccel_dict[key])


        real_accel = Transform(realaccel_dict["x"], realaccel_dict["y"], realaccel_dict["z"])
        world_accel = Transform(worldaccel_dict["x"], worldaccel_dict["y"], worldaccel_dict["z"])



        return IMUData(rotation, real_accel, world_accel)
    except Exception as e:
        print(e)
        logging.getLogger('asyncio').error("IMU read failed.")
        return None

def float_with_2_decimals(value):
    two_decimal_float = float("{0:.2f}".format(value))
    return two_decimal_float