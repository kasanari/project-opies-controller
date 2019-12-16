from kalman.PositionEstimator import PositionEstimator
import asyncio
from asyncio import Queue
import numpy as np
from websocket_server.websocket_server import ToWeb


async def kalman_man(measurement_queue: Queue, estimated_state_queue: Queue, to_web_queue=None, control_queue=None):

    # Initalize Kalman Filter
    measurements = await measurement_queue.get()
    await measurement_queue.put(measurements)
    loc_data, imu_data = measurements

    position_estimator = PositionEstimator(std_dev_acc=0.8, std_dev_position=0.2, std_dev_velocity=0.8, dim_u=2,
                                           dim_x=6, update_delay=0.1)

    position_estimator.start_kalman_filter(loc_data)

    while True:
        try:
            measurements = await asyncio.wait_for(measurement_queue.get(), timeout=1)
            loc_data, imu_data = measurements
            await measurement_queue.put(measurements)
        except asyncio.TimeoutError:
            print("Dead reckoning")
        if control_queue is not None:

            try:
                steering_signal = await control_queue.get()
                control_queue.put_nowait(steering_signal)
                steering_signal = steering_signal.to_numpy()
            except asyncio.QueueEmpty:
                print("No control signal!")
                steering_signal = np.array([0, 0])

        else:
            steering_signal = np.array([0, 0])
        estimated_state = position_estimator.do_kalman_updates(loc_data, imu_data, control_signal=steering_signal)

        estimated_state_queue.put_nowait(estimated_state)

        if to_web_queue is not None:
            to_web = ToWeb("measurements", estimated_state, loc_data, imu_data)
            to_web_queue.put_nowait(to_web)

        await asyncio.sleep(0.1)
