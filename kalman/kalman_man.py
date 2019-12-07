from kalman.kalman_filtering import init_kalman_filter, kalman_updates
import asyncio
import numpy as np



async def kalman_task(measurement_queue, control_queue=None, update_delay=0.1, control_signal=False, dim_u=0):

    # Initalize Kalman Filter
    measurement = await measurement_queue.get()
    kf = init_kalman_filter(measurement, dt=update_delay, covar_x_y=0, dim_u=dim_u)

    while True:
        try:
            measurement = measurement_queue.get_nowait()
        except asyncio.QueueEmpty:
            print("Dead reckoning")
        if control_signal:
            steering_signal = control_queue.get_nowait()
        else:
            steering_signal = np.array([0])
        loc_data_filtered = kalman_updates(kf, measurement, timestep=0.1, u=steering_signal)

        await asyncio.sleep(0.1)