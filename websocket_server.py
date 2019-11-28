import websockets
from websockets import WebSocketServerProtocol, ConnectionClosedError
import asyncio
import json
import random
import datetime
import functools


async def time():  # TODO change this to send location info as well as time
    """Generates a message containing the location of the Pi and the current time"""
    await asyncio.sleep(1)  # To simulate a delay in getting the location data
    data_to_send = {
        'x': random.randint(0, 10),
        'y': random.randint(0, 10),
        'timestamp': datetime.datetime.utcnow().isoformat()
    }

    return json.dumps(data_to_send)


def create_websocket_task(ip_addr, message_queue, location_queue):
    """Creates a task for running the websocket server"""
    handler_func = functools.partial(handler, message_queue=message_queue, location_queue=location_queue)

    return websockets.serve(handler_func, ip_addr, 5678)


async def send_handler(websocket, path, location_queue):
    """ Sends location data (only time currently) to client """
    print("Client Connected!")
    while True:
        loc_message, loc_filtered_message = await location_queue.get()
        loc_dict = {
            'x': loc_message.x,
            'x_kf': loc_filtered_message.x,
            'y': loc_message.y,
            'y_kf': loc_filtered_message.y,
            'quality': loc_message.quality
        }
        await websocket.send(json.dumps(loc_dict)) #filtered_message.get_as_dict()))


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


async def handler(websocket: WebSocketServerProtocol, path: str, message_queue, location_queue):
    """ Starts all tasks related to websockets and motor control"""
    receive_msg_task = asyncio.create_task(receive_handler(websocket, path, message_queue))
    send_msg_task = asyncio.create_task(send_handler(websocket, path, location_queue))

    done, pending = await asyncio.wait([receive_msg_task, send_msg_task], return_when=asyncio.FIRST_COMPLETED)
    print("Client Disconnected!")
    for task in pending:
        task.cancel()