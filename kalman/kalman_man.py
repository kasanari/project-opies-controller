import logging

from analysis.data_logger import DataLogger

from kalman.PositionEstimator import PositionEstimator
import asyncio

from application.context import ControlSignal, Context
from websocket_server.websocket_server import ToWeb


async def kalman_man(context: Context):
    try:
        # Initalize Kalman Filter
        logging.getLogger('asyncio').info("Initializing.")
        await context.new_measurement_event.wait()
        measurements = context.measurement
        loc_data, imu_data = measurements
        context.new_measurement_event.clear()

        data_logger = DataLogger()
        position_estimator = PositionEstimator(std_dev_acc=0.8, std_dev_position=0.25, std_dev_velocity=0.8, dim_u=0,
                                               dim_x=6, update_delay=0.2)

        position_estimator.start_kalman_filter(loc_data)

        while True:

            try:
                logging.getLogger('asyncio').info("Waiting for new measurements.")
                await context.new_measurement_event.wait()
                measurements = context.measurement
                loc_data, imu_data = context.measurement

            except asyncio.TimeoutError:
                print("Dead reckoning")

            if context.auto_steering:
                logging.getLogger('asyncio').info("Waiting for control signal.")
                await context.new_control_signal_event.wait()
                control_signal = context.control_signal
                context.new_control_signal_event.clear()
            else:
                control_signal = ControlSignal()
                context.new_measurement_event.clear()
                context.new_estimated_state_event.clear()

            estimated_state = position_estimator.do_kalman_updates(loc_data, imu_data,
                                                                   control_signal=control_signal.to_numpy(),
                                                                   variable_dt=True)

            context.estimated_state = estimated_state
            context.new_estimated_state_event.set()

            data_logger.log_data(measurements, estimated_state, control_signal)


            to_web = ToWeb("measurements", estimated_state, loc_data, imu_data)
            context.to_web_queue.put_nowait(to_web)

    except asyncio.CancelledError:

        logging.getLogger('asyncio').info(f"Cancelled.")
        data_logger.make_directory()
        data_logger.save_csv()
        data_logger.create_plots()
