#!/usr/bin/python
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import asyncio
import websockets
from websockets import WebSocketServerProtocol
import datetime
import random
import threading
import json
from motor_control import Steering

PORT_NUMBER = 8080
IP = "192.168.1.251"
steering = Steering(17)

async def order(message):  # TODO add proper order handling
    message = json.loads(message)
    print(message)
    angle = int(message["angle"])
    print(angle)
    steering.set_angle(angle)


async def order_handler(websocket, path):
    async for message in websocket:
        await order(message)


async def time():  # TODO change this to send location info as well as time
    return f"{datetime.datetime.utcnow().isoformat()}: X={random.randint(0, 10)} Y={random.randint(0, 10)}"


async def time_handler(websocket, path):
    while True:
        message = await time()
        await websocket.send(message)
        await asyncio.sleep(1)


async def handler(websocket: WebSocketServerProtocol, path: str):
    consumer_task = asyncio.create_task(order_handler(websocket, path))
    producer_task = asyncio.create_task(time_handler(websocket, path))

    done, pending = await asyncio.wait([consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()


def start_websocket_server():
    print("Starting Websocket Server")
    start_server = websockets.serve(handler, IP, 5678)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


def start_http_server():
    server_address = ('', PORT_NUMBER)
    HTTPServer(server_address, SimpleHTTPRequestHandler).serve_forever()


print(f"Starting HTTP Server at port {PORT_NUMBER}")
daemon = threading.Thread(name='daemon_server', target=start_http_server)
daemon.setDaemon(True)  # Set as a daemon so it will be killed once the main thread is dead.
daemon.start()

start_websocket_server()

