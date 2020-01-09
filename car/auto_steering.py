import asyncio
import logging
import math
import time

import numpy as np
import pandas as pd
from serial import Serial

import pathfinding.pathing as pathing
import pathfinding.pure_pursuit as pp
from analysis.data_logger import DataLogger
from application.context import Target, Context
from arduino_interface import arduino_serial
from arduino_interface.imu import IMUData
from arduino_interface.ultrasonic import measure_distance
from car.pidcontroller import PIDController
from serial_with_dwm.location_data_handler import LocationData
from websocket_server.websocket_server import ToWeb


def position_error(target_x, target_y, x, y):
    y_diff = target_y - y
    x_diff = target_x - x
    return y_diff, x_diff


def angle_error(target_x, target_y, x, y):
    x_diff = target_x - x
    y_diff = target_y - y
    print(f"x_diff: {x_diff}")
    print(f"y_diff: {y_diff}")
    angle = (np.arctan2(y_diff, x_diff) - np.pi / 2) * -1
    return np.rad2deg(angle)


def check_for_collision(connection, limit):
    distance = measure_distance(connection)
    print(f"Distance in CM: {distance}")

    if distance < limit:
        return True


def logger(self, **kwargs):
    # location = location.get_as_dict()
    time_stamp = pd.Timestamp.utcnow()
    self.data_log = self.data_log.append(pd.DataFrame(kwargs, index=[time_stamp]))


def calculate_lyapunov_errors(target: Target, position: LocationData, angle):
    x_diff = target.x - position.x
    y_diff = target.y - position.y
    x = np.cos(angle) * x_diff + np.sin(angle) * y_diff
    y = -np.sin(angle) * x_diff + np.cos(angle) * y_diff
    theta = target.yaw - angle
    return x_diff, y_diff, theta


async def auto_steer_task(context: Context,
                          rc_car,
                          movie_filename=None):

    loc_data: LocationData
    imu_data: IMUData
    arduino_connection: Serial
    print("Auto steering started.")
    log = logging.getLogger('asyncio')

    path_points = context.settings["path"]

    checkpoint_threshold = 0.75
    goal_threshold = 0.35

    points_x = path_points["x"]
    points_y = path_points["y"]


    path = pathing.Path(points_x, points_y)

    checkpoints = [False for _ in points_x]

    data_logger = DataLogger()
    steering_controller = PIDController(**context.settings["pid"]["steering"])
    speed_controller = PIDController(**context.settings["pid"]["speed"])



    try:
        while True:

            log.info("Waiting for estimated state and measurements")
            await context.new_estimated_state_event.wait()
            estimated_state = context.estimated_state
            loc_data = estimated_state.location_est
            log.info("Calculating control signal.")

            if context.settings["kalman"]["uwb_only_kf"]:
                _, imu_data = estimated_state.measurement.result_tag, estimated_state.measurement.result_imu
                yaw = imu_data.rotation.yaw
            else:
                yaw = estimated_state.yaw_est

            context.new_estimated_state_event.clear()

            for i, (x, y) in enumerate(zip(points_x, points_y)):
                if checkpoints[i] is not True:
                    dx = x - loc_data.x
                    dy = y - loc_data.y
                    distance_to_checkpoint = math.hypot(dx, dy)
                    if distance_to_checkpoint < checkpoint_threshold:
                        print(f"Reeached checkpoint {i}")
                        checkpoints[i] = True

            if not (False in checkpoints):
                print("All checkpoints passed!")
                dx = points_x[-1] - loc_data.x
                dy = points_y[-1] - loc_data.y
                distance_to_goal = math.hypot(dx, dy)
                if distance_to_goal < goal_threshold:
                    context.auto_steering = False
                    context.new_control_signal_event.set()
                    await rc_car.brake()
                    rc_car.stop()
                    print(f"Reached goal at {(path_points['x'][-1], path_points['y'][-1])}.")
                    return

            l = context.settings["lookahead"]

            if len(path) > 1:
                 tx, ty = pp.find_nearest_point(loc_data.x, loc_data.y, l, path)
            else:
                tx, ty = path.x[0], path.y[0]

            alpha, t_theta = pp.get_alpha(loc_data.x, loc_data.y, yaw, tx, ty)

            u_angle = steering_controller.get_control_signal(alpha, time.time())

            speed = math.hypot(estimated_state.y_v_est, estimated_state.x_v_est)
            target_speed = 0.5
            speed_error = target_speed - speed
            u_speed = 0.16 + speed_controller.get_control_signal(speed_error, time.time())
            if u_speed > 0.18:
                u_speed = 0.18
            elif u_speed < 0.16:
                u_speed = 0.16

            #log.info(f"distance_to_goal: {distance_to_goal}")
            log.debug(f"alpha: {alpha}")
            log.debug(f"acceleration: {u_speed}")
            log.debug(f"u_angle: {u_angle}")

            context.control_signal.steering = u_angle
            context.control_signal.velocity = u_speed
            context.control_signal.target = Target(tx, ty, yaw=t_theta)
            context.control_signal.error.yaw = alpha

            rc_car.set_wheel_angle(u_angle)
            rc_car.set_acceleration(u_speed)

            data_logger.log_data(estimated_state, context.control_signal)

            context.new_control_signal_event.set()


    except asyncio.CancelledError as e:
        log.warning(e)
        await rc_car.brake()
        rc_car.stop()
        print("Auto steer cancelled.")

    except Exception as e:
        log.error(e)

    finally:

        context.auto_steering = False

        logging.getLogger('asyncio').info(f"Cancelled.")
        data_logger.make_directory()
        data_logger.save_csv()
        data_logger.create_plots()
        if context.settings["generate_movie"]:
            try:
                data_logger.plot_path(path_points=context.settings["path"],
                                      lookahead=context.settings["lookahead"],
                                      movie_filename=movie_filename)

                to_web = ToWeb("movie")
                context.to_web_queue.put_nowait(to_web)
            except KeyError as e:
                print(e)
                print("Path plot failed due to missing data")
        return True
