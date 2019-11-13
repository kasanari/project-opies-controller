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

def create_websocket_task(ip_addr, queue):
    handler_func = functools.partial(handler, queue=queue)
    return websockets.serve(handler_func, ip_addr, 5678)

async def send_handler(websocket, path):
    """ Sends location data (only time currently) to client """
    print("Client Connected!")
    while True:
        message = await time()
        await websocket.send(message)


async def receive_handler(websocket, path, queue):
    """ Handles incoming messages from client """
    try:
        async for message in websocket:
            message = json.loads(message)
            await queue.put(message)
    except ConnectionClosedError:
        message = {'type': 'stop'}
        queue.put(message)
        return


async def handler(websocket: WebSocketServerProtocol, path: str, queue):
    """ Starts all tasks related to websockets and motor control"""
    receive_msg_task = asyncio.create_task(receive_handler(websocket, path, queue))
    send_msg_task = asyncio.create_task(send_handler(websocket, path))

    done, pending = await asyncio.wait([receive_msg_task, send_msg_task], return_when=asyncio.FIRST_COMPLETED)
    print("Client Disconnected!")
    for task in pending:
        task.cancel()