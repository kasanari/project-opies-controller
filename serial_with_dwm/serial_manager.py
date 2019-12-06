import asyncio
import arduino_interface.imu as imu
import arduino_interface.arduino_serial as arduino
import concurrent.futures
import functools
import datetime
import serial
from serial_with_dwm.serial_handler import SerialHandler


def fetch_location_data(ser_handler):

    loc_data = ser_handler.get_location_data()  # serial connection with dwm1001, get location data

    return loc_data


async def serial_man():
    ser_con = None
    arduino_con = None

    try:
        while True:
            arduino_con = arduino.connect_to_arduino()

            try:
                ser_con = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=1)
            except serial.SerialException:
                print("Failed to connect to tag")

            success = await imu.start_IMU(arduino_con)

            ser_handler = SerialHandler(ser_con)

            read_imu = functools.partial(imu.read_IMU, connection=arduino_con)
            read_tag = functools.partial(fetch_location_data, ser_handler=ser_handler)

            event_loop = asyncio.get_running_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:


                result_imu_task = event_loop.run_in_executor(pool, read_imu)
                result_tag_task = event_loop.run_in_executor(pool, read_tag)
                result_imu, result_tag = await asyncio.gather(result_imu_task, result_tag_task)



            print(result_tag)

            ypr, realaccel, worldaccel = result_imu
            print(f"ypr: {ypr}")
            print(f"real_accel: {realaccel}")
            print(f"worl_accel: {worldaccel}")
            print("--------")

            #dt_measurements = update_delay + seconds
            #steering_signal = np.array([1])  # temp
            #loc_data_filtered = kalman_updates(kf, loc_data, dt_measurements, u=steering_signal)
            #tasks = [q.put([loc_data, loc_data_filtered]) for q in queues]

    except asyncio.CancelledError:
        print("Task cancelled.")
    finally:
        if ser_con is not None:
            ser_con.close()
        if arduino_con is not None:
            arduino_con.close()

if __name__ == "__main__":
     asyncio.run(serial_man())