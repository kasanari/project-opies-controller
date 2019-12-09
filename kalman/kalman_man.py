from kalman.kalman_filtering import init_kalman_filter, kalman_updates
import asyncio
from asyncio import Queue
import numpy as np
from websocket_server.websocket_server import ToWeb


async def kalman_man(measurement_queue: Queue, estimated_state_queue: Queue, to_web_queue=None, control_queue=None, update_delay=0.1, dim_u=0):

    # Initalize Kalman Filter
    measurements = await measurement_queue.get()
    await measurement_queue.put(measurements)
    loc_data, imu_data = measurements

    kf = init_kalman_filter(loc_data, dt=update_delay, covar_x_y=0, dim_u=dim_u)

    while True:
        try:
            measurements = measurement_queue.get_nowait()
            loc_data, imu_data = measurements
            measurement_queue.put_nowait(measurements)
        except asyncio.QueueEmpty:
            print("Dead reckoning")
        if control_queue is not None:
            steering_signal = control_queue.get_nowait()
        else:
            steering_signal = np.array([0])
        loc_data_filtered = kalman_updates(kf, loc_data, timestep=0.1, u=steering_signal)
        estimated_state_queue.put_nowait(loc_data_filtered)

        if to_web_queue is not None:
            to_web = ToWeb("measurements", loc_data_filtered, loc_data, imu_data)
            to_web_queue.put_nowait(to_web)

        await asyncio.sleep(0.1)
