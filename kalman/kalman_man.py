import asyncio
import logging

from analysis.data_logger import DataLogger
from application.context import ControlSignal, Context
from kalman.PositionEstimator import PositionEstimator
from websocket_server.websocket_server import ToWeb


async def kalman_man(context: Context):
    data_logger = DataLogger()
    try:
        # Initalize Kalman Filter
        logging.getLogger('asyncio').info("Initializing.")
        await context.new_measurement_event.wait()
        measurement = context.measurement
        loc_data, imu_data = measurement.result_tag, measurement.result_imu
        context.new_measurement_event.clear()

        position_estimator = PositionEstimator(**context.settings["kalman"])

        position_estimator.start_kalman_filter(loc_data)

        while True:

            try:
                logging.getLogger('asyncio').info("Waiting for new measurements.")
                await context.new_measurement_event.wait()
                measurement = context.measurement
                loc_data, imu_data = measurement.result_tag, measurement.result_imu
                context.new_measurement_event.clear()

            except asyncio.TimeoutError:
                print("Dead reckoning")

            if context.auto_steering:
                logging.getLogger('asyncio').info("Waiting for control signal.")
                await context.new_control_signal_event.wait()
                if context.auto_steering:
                    control_signal = context.control_signal
                    context.new_control_signal_event.clear()
            else:
                control_signal = ControlSignal()
                context.new_measurement_event.clear()
                context.new_estimated_state_event.clear()

            estimated_state = position_estimator.do_kalman_updates(loc_data, imu_data,
                                                                   control_signal=control_signal.to_numpy(),
                                                                   variable_dt=True)
            estimated_state.measurement = measurement
            context.estimated_state = estimated_state
            context.new_estimated_state_event.set()

            data_logger.log_data(estimated_state, control_signal)


            to_web = ToWeb("measurements", estimated_state, loc_data, imu_data)
            context.to_web_queue.put_nowait(to_web)

    except asyncio.CancelledError:

        logging.getLogger('asyncio').info(f"Cancelled.")
        data_logger.make_directory()
        data_logger.save_csv()
        data_logger.create_plots()
        if context.settings["generate_movie"]:
            try:
                data_logger.plot_path(path_points=context.settings["path"], lookahead=context.settings["lookahead"])
            except KeyError as e:
                print(e)
                print("Path plot failed due to missing data")
        return True




