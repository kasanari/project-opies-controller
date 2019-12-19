import asyncio
import concurrent.futures
import datetime
import functools
import logging
from asyncio import Queue

import serial

import arduino_interface.arduino_serial as arduino
import arduino_interface.imu as imu
from application.context import Context
from serial_with_dwm.serial_handler import SerialHandler


def fetch_location_data(ser_handler):
    serial_collect_time_start = datetime.datetime.now()
    loc_data = ser_handler.get_location_data()  # serial connection with dwm1001, get location data
    if loc_data is None:
        logging.getLogger('asyncio').warning("Location data was None!")
    serial_collect_time_end = datetime.datetime.now()
    serial_collect_time_total = serial_collect_time_end - serial_collect_time_start
    seconds = serial_collect_time_total.total_seconds()  # ceiling? milliseconds = int(seconds * 1000)
    return loc_data, seconds


async def serial_man(context: Context, update_delay: float = 0.3):
    ser_con = None
    arduino_con = None

    try:
        arduino_con = arduino.connect_to_arduino()
        success = await imu.start_IMU(arduino_con)

        if not success:
            logging.getLogger('asyncio').warning("Failed to setup IMU")
        try:
            ser_con = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=1)

        except serial.SerialException:
            logging.getLogger('asyncio').warning("Failed to connect to tag")

        ser_handler = SerialHandler(ser_con)
        read_imu = functools.partial(imu.read_IMU, connection=arduino_con)
        read_tag = functools.partial(fetch_location_data, ser_handler=ser_handler)

        event_loop = asyncio.get_running_loop()

        while True:
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result_imu_task = event_loop.run_in_executor(pool, read_imu)
                result_tag_task = event_loop.run_in_executor(pool, read_tag)
                logging.getLogger('asyncio').info("Waiting for tag and IMU.")
                result_imu, result_tag = await asyncio.gather(result_imu_task, result_tag_task)
            # print(result_tag[0])
            # print(result_tag[1])

            # print(result_imu)
            # print(result_tag)
            context.measurement = [result_tag[0], result_imu]
            context.new_measurement_event.set()

            # print(result_tag)

            # ypr, realaccel, worldaccel = result_imu
            # print(f"ypr: {ypr}")
            # print(f"real_accel: {realaccel}")
            # print(f"worl_accel: {worldaccel}")
            # print("--------")
            # logging.getLogger('asyncio').info(f"Serial Man: Sleeping for {update_delay} seconds.")
            await asyncio.sleep(0.05)

            # dt_measurements = update_delay + seconds
            # steering_signal = np.array([1])  # temp
            # loc_data_filtered = kalman_updates(kf, loc_data, dt_measurements, u=steering_signal)
            # tasks = [q.put([loc_data, loc_data_filtered]) for q in queues]

    except asyncio.CancelledError:
        logging.getLogger('asyncio').info(f"Cancelled.")
    finally:
        if ser_con is not None:
            ser_con.close()
        if arduino_con is not None:
            arduino_con.close()


if __name__ == "__main__":
    state_queue = Queue()
    asyncio.run(serial_man(state_queue, update_delay=0.3))
