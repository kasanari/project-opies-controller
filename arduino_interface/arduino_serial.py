import serial
import asyncio
import functools
import concurrent.futures
import arduino_interface.imu as imu


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
        raise serial.SerialException

    return ser


async def main(connection):
    success = await imu.start_IMU(connection)

    while 1:
        loop = asyncio.get_running_loop()
        read_imu = functools.partial(imu.read_IMU, connection=connection)
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result: imu.IMUData = await loop.run_in_executor(pool, read_imu)
        print(f"ypr: {result.rotation}")
        print(f"real_accel: {result.real_acceleration}")
        print(f"worl_accel: {result.world_acceleration}")
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
