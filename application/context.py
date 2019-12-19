from asyncio.locks import Event
from asyncio.queues import Queue
from dataclasses import dataclass

import numpy as np

from application.settings import load_settings, load_default_settings
from arduino_interface.imu import IMUData
from kalman.kalman_filtering import EstimatedState
from serial_with_dwm.location_data_handler import LocationData


@dataclass
class Target:
    x: float
    y: float
    yaw: float
    velocity: float


@dataclass
class ControlSignal:
    velocity: float = 0
    steering: float = 0
    target: Target = Target(0, 0, 0, 0)
    error: Target = Target(0, 0, 0, 0)

    def to_numpy(self):
        return np.array([self.velocity, self.steering])


@dataclass
class Context:
    new_measurement_event: Event
    new_estimated_state_event: Event
    new_control_signal_event: Event
    settings: dict
    to_web_queue: Queue
    from_web_queue: Queue
    measurement: (LocationData, IMUData) = None
    control_signal = ControlSignal(0, 0, Target(0, 0, 0, 0))
    estimated_state: EstimatedState = None
    auto_steering = False

    def __init__(self, settings_file = None):

        self.new_control_signal_event = Event()
        self.new_estimated_state_event = Event()
        self.new_measurement_event = Event()
        self.to_web_queue = Queue()
        self.from_web_queue = Queue()

        self.new_control_signal_event.set()

        if settings_file is None:
            self.settings = load_default_settings()
        else:
            self.settings = load_settings(settings_file)



    async def get_estimated_state(self):
        await self.new_estimated_state_event.wait()
        return self.estimated_state


settings = None

