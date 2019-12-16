import logging

from analysis.data_logger import DataLogger
from kalman.kalman_filtering import init_kalman_filter, kalman_updates
import asyncio

from application import Context
from websocket_server.websocket_server import ToWeb


async def kalman_man(context: Context, update_delay=0.1, dim_u=0, dim_x=6, use_acc=True):
    # Initalize Kalman Filter
    measurements = await context.new_measurement_event.wait()
    loc_data, imu_data = context.measurement

    kf = init_kalman_filter(loc_data, dt=update_delay, dim_x=dim_x, dim_u=dim_u, use_acc=use_acc)

    rc_car = Car()

    auto_pilot = AutoPilot(rc_car)

    data_logger = DataLogger()

    while True:

        try:
            logging.getLogger('asyncio').info("Waiting for new measurements.")
            measurements = await context.new_measurement_event.wait()
            loc_data, imu_data = context.measurement

        except asyncio.TimeoutError:
            print("Dead reckoning")

        await context.new_control_signal_event.wait()
        control_signal = context.control_signal

        estimated_state = kalman_updates(kf, loc_data, imu_data, u=control_signal, timestep=0.1, use_acc=use_acc)

        context.estimated_state = estimated_state
        context.new_measurement_event.set()

        data_logger.log_data(measurements, estimated_state, control_signal)

        to_web = ToWeb("measurements", estimated_state, loc_data, imu_data)
        context.to_web_queue.put_nowait(to_web)

        logging.getLogger('asyncio').info("Sleeping.")
        await asyncio.sleep(0.1)
