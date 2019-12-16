from dataclasses import dataclass
import numpy as np
from arduino_interface.imu import IMUData
from kalman.kalman_filtering import EstimatedState
from serial_with_dwm.location_data_handler import LocationData
from asyncio import Event, Queue

@dataclass
class Target:
    x: float
    y: float
    yaw: float
    velocity: float

@dataclass
class ControlSignal:
    velocity: float
    steering: float
    target: Target = None

    def to_numpy(self):
        return np.array([self.velocity, self.steering])

@dataclass
class Context:
    measurement: (LocationData, IMUData) = None
    control_signal = ControlSignal(0, 0)
    estimated_state: EstimatedState = None
    auto_steering = False
    new_measurement_event: Event = Event()
    new_estimated_state_event: Event = Event()
    new_control_signal_event: Event = Event()
    to_web_queue: Queue = Queue()
    from_web_queue: Queue = Queue()

    async def get_estimated_state(self):
        await self.new_estimated_state_event.wait()
        return self.estimated_state
