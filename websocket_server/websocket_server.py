import websockets
from websockets import WebSocketServerProtocol, ConnectionClosedError
import asyncio
import json
import random
import datetime
import functools
from serial_with_dwm.location_data_handler import LocationData
from kalman.kalman_filtering import EstimatedState
from arduino_interface.imu import IMUData
from dataclasses import dataclass, asdict
import logging

@dataclass
class ToWeb:
    type: str
    estimated_state: EstimatedState
    location_measurements: LocationData
    imu_measurements: IMUData
    anchors = None

    def generate_json_msg(self):
        msg_dict = {'type': self.type}

        if self.location_measurements is not None:
            msg_dict['estimation'] = asdict(self.estimated_state)
        else:
            msg_dict['estimation'] = {}

        if self.location_measurements.get_as_dict() is not None:
            msg_dict['location'] = self.location_measurements.get_as_dict()
        else:
            msg_dict['location'] = {}

        if self.location_measurements.get_as_dict() is not None:
            msg_dict['imu'] = asdict(self.imu_measurements)
        else:
            msg_dict['imu'] = {}

        if self.anchors is not None:
            msg_dict['anchors'] = [asdict(anchor) for anchor in self.anchors]
        else:
            msg_dict['anchors'] = {}

        return json.dumps(msg_dict)


async def time():  # TODO change this to send location info as well as time
    """Generates a message containing the location of the Pi and the current time"""
    await asyncio.sleep(1)  # To simulate a delay in getting the location data
    data_to_send = {
        'x': random.randint(0, 10),
        'y': random.randint(0, 10),
        'timestamp': datetime.datetime.utcnow().isoformat()
    }

    return json.dumps(data_to_send)


def create_websocket_task(context, ip_addr):
    """Creates a task for running the websocket server"""
    handler_func = functools.partial(handler, context=context)

    return websockets.serve(handler_func, ip_addr, 5678)


async def send_handler(websocket, path, send_queue):
    """ Sends location data (only time currently) to client """
    print("Client Connected!")
    while True:
        message: ToWeb = await send_queue.get()
        await websocket.send(message.generate_json_msg())  # filtered_message.get_as_dict()))


async def receive_handler(websocket, path, queue):
    """ Handles incoming messages from client """
    try:
        async for message in websocket:
            message = json.loads(message)
            await queue.put(message)
    except ConnectionClosedError:
        message = {'type': 'stop'}
        await queue.put(message)
        return


async def handler(websocket: WebSocketServerProtocol, path: str, context):
    """ Starts all tasks related to websockets and motor control"""
    try:
        receive_msg_task = asyncio.create_task(receive_handler(websocket, path, context.from_web_queue))
        send_msg_task = asyncio.create_task(send_handler(websocket, path, context.to_web_queue))

        done, pending = await asyncio.wait([receive_msg_task, send_msg_task], return_when=asyncio.FIRST_COMPLETED)
        print("Client Disconnected!")
        for task in pending:
            task.cancel()
    except asyncio.CancelledError:
        logging.getLogger('asyncio').info("Cancelling websocket tasks")
    finally:
        for task in pending:
            task.cancel()