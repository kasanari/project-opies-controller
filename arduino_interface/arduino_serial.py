import serial
import asyncio
import csv
import io
import re
import functools
import concurrent.futures

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

    ypr_dict = {"yaw": float(ypr[0]), "pitch": float(ypr[1]), "roll": float(ypr[2])}

    realaccel_dict = {"x": realaccel[0], "y": realaccel[1], "z": realaccel[2]}
    worldaccel_dict = {"x": worldaccel[0], "y": worldaccel[1], "z": worldaccel[2]}

    realaccel_dict = convert_g_to_acceleration(realaccel_dict)
    worldaccel_dict = convert_g_to_acceleration(worldaccel_dict)

    return ypr_dict, realaccel_dict, worldaccel_dict


def connect_to_arduino():
    ser = None
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2)
    except serial.SerialException:

        for i in range(1, 5):
            try:
                ser = serial.Serial(f'/dev/ttyUSB{i}', 115200, timeout=2)
            except serial.SerialException:
                pass

    if ser is None:
        raise RuntimeError

    return ser


def measure_distance(connection):
    line = b''

    while line == b'':
        msg = "a\n".encode()
        connection.write(msg)
        line = connection.readline()

    return int(line)


async def start_IMU(connection):
    try:
        await asyncio.wait_for(calibrate_IMU(connection), timeout=10)
    except asyncio.TimeoutError:
        print("IMU setup timed out.")
        return False

    return True


async def main(connection):
    success = await start_IMU(connection)

    while 1:
        loop = asyncio.get_running_loop()
        read_imu = functools.partial(read_IMU, connection=connection)
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, read_imu)
        ypr, realaccel, worldaccel = result
        print(f"ypr: {ypr}")
        print(f"real_accel: {realaccel}")
        print(f"worl_accel: {worldaccel}")
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
