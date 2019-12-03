import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import asyncio
import csv
import argparse
from car.motor_control import motor_control_task
from serial_with_dwm.serial_handler import serial_task
from serial_with_dwm.location_data_handler import LocationData

matplotlib.use('Agg')
sleep_time = 20


def create_plots(dataframe, filename_timestamp):
    dataframe.plot(x=['x', 'x_kf'], y=['y', 'y_kf'], kind='scatter')
    plt.ylim(0, 5)
    plt.xlim(0, 5)
    plt.savefig(f"{filename_timestamp}_collect_data_scatter_plot.png")

    #Line plot
    dataframe.reset_index().plot(x='index', y=['x','y', 'target_x', 'target_y', 'x_kf', 'y_kf'])

    plt.savefig(f"{filename_timestamp}_collect_data_line_plot_xy.png")


async def fake_serial_task(data_file, *queues, update_delay=1):
    with open(data_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            location_data = LocationData(float(row['x']), float(row['y']), 0, float(row['quality']))
            tasks = [q.put(location_data) for q in queues]
            await asyncio.gather(*tasks)
            await asyncio.sleep(update_delay)


async def log_task(location_queue):
    location_df = pd.DataFrame()
    try:
        while True:
            location, location_filtered = await location_queue.get()

            locations = {
                'x': location.x,
                'y': location.y,
                'target_y': 2.5,
                'target_x': 1.8,
                'quality': location.quality,
                'x_kf': location_filtered.x,
                'y_kf': location_filtered.y
            }
            print(f"logging task: x is {location.x}")
            print(f"logging task: x_kf is {location_filtered.x}")
            print(f"quality is {location.quality}")
            time_stamp = pd.Timestamp.utcnow()
            location_df = location_df.append(pd.DataFrame(locations, index=[time_stamp]))

    except asyncio.CancelledError:
        print("Logging cancelled")
        return location_df


async def main(data_file=None, disable_motor=True, no_saving=False, out_file=None) :
    message_queue = asyncio.Queue()
    serial_queue = asyncio.Queue()
    log_queue = asyncio.Queue()
    motor_task = None

    if data_file is None:
        location_task = asyncio.create_task(serial_task(log_queue, serial_queue)) # use real serial
    else:
        location_task = asyncio.create_task(fake_serial_task(data_file, log_queue, serial_queue)) #get data from file

    if not disable_motor:
        message = {'type': "destination", 'x': 0.8, 'y': 10}
        await message_queue.put(message)
        motor_task = asyncio.create_task(motor_control_task(message_queue, serial_queue))

    logging_task = asyncio.create_task(log_task(log_queue))

    if data_file is None: #If we are using real serial, collect data for 7 seconds and then cancel the task
        await asyncio.sleep(sleep_time)
        location_task.cancel()
    else: #otherwise we just wait for the task to finish reading the file
        await location_task

    if not disable_motor and motor_task is not None:
        motor_task.cancel()

    logging_task.cancel()
    result : pd.DataFrame = await logging_task

    file_timestamp = generate_timestamp()
    if not no_saving:
        if out_file is None:
            result.to_csv(f'{file_timestamp}.csv')
        else:
            result.to_csv(out_file)

    create_plots(result, file_timestamp)

    print("Done")


def generate_timestamp():
    timestamp = pd.Timestamp.utcnow().ctime()
    timestamp = str(timestamp).replace(" ", "_")
    timestamp = timestamp.replace(":", "")
    return timestamp

if __name__ == "__main__":


    parser = argparse.ArgumentParser(description='Collect location data for analysis.')
    parser.add_argument('--fake_serial', nargs='?', help='Use saved data instead of serial connection')
    parser.add_argument('--disable_motor', action='store_true', help='disable the motor control task')
    parser.add_argument("-o", nargs='?', dest="out_file", help="output file name, in csv format. Defaults to a timestamp.")
    parser.add_argument("--no_saving", dest='no_saving', action='store_true', help="Disables saving results to a file")

    args = parser.parse_args()

    data_file = args.fake_serial
    disable_motor = args.disable_motor
    out_file = args.out_file
    no_saving = args.no_saving

    asyncio.run(main(data_file, disable_motor, no_saving, out_file))
