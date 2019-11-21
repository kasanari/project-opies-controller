import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import asyncio
import csv
import argparse
from motor_control import motor_control_task
from serial_handler import serial_task
from location_data_handler import LocationData

matplotlib.use('Agg')

def create_plots(dataframe):
    dataframe.plot(x="x", y="y", kind='scatter')

    plt.savefig("scatter_plot.png")

    dataframe.reset_index().plot(x='index', y=['x','y'])

    plt.savefig("line_plot.png")



async def fake_serial_task(data_file, *queues):
    with open(data_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            location_data = LocationData(float(row['x']), float(row['y']), float(row['z']), float(row['quality']))
            tasks = [q.put(location_data) for q in queues]
            await asyncio.gather(*tasks)


async def log_task(location_queue):
    location_df = pd.DataFrame()
    try:
        while True:
            location = await location_queue.get()

            location = location.get_as_dict()
            time_stamp = pd.Timestamp.utcnow()
            location_df = location_df.append(pd.DataFrame(location, index=[time_stamp]))

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
        message = {'type': "destination", 'x': 0, 'y': 1.5}
        await message_queue.put(message)
        motor_task = asyncio.create_task(motor_control_task(message_queue, serial_queue))

    logging_task = asyncio.create_task(log_task(log_queue))

    if data_file is None: #If we are using real serial, collect data for 7 seconds and then cancel the task
        await asyncio.sleep(7)
        location_task.cancel()
    else: #otherwise we just wait for the task to finish reading the file
        await location_task

    if not disable_motor and motor_task is not None:
        motor_task.cancel()

    logging_task.cancel()
    result : pd.DataFrame = await logging_task

    if not no_saving:
        if out_file is None:
            timestamp = pd.Timestamp.utcnow().ctime()
            timestamp = str(timestamp).replace(" ", "_")
            timestamp = timestamp.replace(":", "")
            result.to_csv(f'{timestamp}.csv')
        else:
            result.to_csv(out_file)

    create_plots(result)

    print("Done")


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
