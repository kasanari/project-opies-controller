import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import asyncio
from motor_control import motor_control_task
from serial_handler import serial_task
from location_data_handler import LocationData

matplotlib.use('Agg')


async def log_task(location_queue):
    location_df = pd.DataFrame()
    try:
        while True:
            location = await location_queue.get()

            location = location.get_as_dict()
            time_stamp = pd.Timestamp.utcnow()
            location_df = location_df.append(pd.DataFrame(location, index=[time_stamp]))

            print(location_df)

    except asyncio.CancelledError:
        print("Logging cancelled")
        return location_df




async def main():
    message_queue = asyncio.Queue()
    serial_queue = asyncio.Queue()
    log_queue = asyncio.Queue()

    location_task = asyncio.create_task(serial_task(log_queue, serial_queue))
    #motor_task = asyncio.create_task(motor_control_task(message_queue, serial_queue))
    logging_task = asyncio.create_task(log_task(log_queue))

    message = {'type': "destination", 'x': 0, 'y': 1.5}
    await message_queue.put(message)

    #await asyncio.gather(location_task, motor_task)
    await asyncio.sleep(7)

    #await logging_task

    location_task.cancel()
    result = location_task.result()
    #motor_task.cancel()
    logging_task.cancel()

    print("Done")


if __name__ == "__main__":

    asyncio.run(main())

    x = [1, 3, 4]
    y = [4, 5, 6]
    plt.plot(x,y)
    plt.savefig('plt.png')
    pass
