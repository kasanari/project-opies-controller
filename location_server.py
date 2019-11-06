#!/usr/bin/python
from http.server import HTTPServer, BaseHTTPRequestHandler, SimpleHTTPRequestHandler
import asyncio
import websockets
from websockets import WebSocketServerProtocol
import datetime
import random
import threading
from main import motor_control_task

PORT_NUMBER = 8080
IP = "192.168.1.251"

async def order_handler(websocket, path, queue):
    async for message in websocket:
        await queue.put(message)


async def time():  # TODO change this to send location info as well as time
    await asyncio.sleep(1)
    return f"{datetime.datetime.utcnow().isoformat()}: X={random.randint(0, 10)} Y={random.randint(0, 10)}"


async def time_handler(websocket, path):
    print("Client Connected!")
    while True:
        message = await time()
        await websocket.send(message)


async def handler(websocket: WebSocketServerProtocol, path: str):
    queue = asyncio.Queue()
    consumer_task = asyncio.create_task(order_handler(websocket, path, queue))
    producer_task = asyncio.create_task(time_handler(websocket, path))
    motor_task = asyncio.create_task(motor_control_task(queue))

    done, pending = await asyncio.wait([consumer_task, producer_task, motor_task], return_when=asyncio.FIRST_COMPLETED)
    print("Client Disconnected!")
    for task in pending:
     task.cancel()


def start_websocket_server():
    print("Starting Websocket Server")
    return websockets.serve(handler, IP, 5678)


def start_http_server():
    server_address = ('', PORT_NUMBER)
    HTTPServer(server_address, SimpleHTTPRequestHandler).serve_forever()

def start_web_client():
    print(f"Starting HTTP Server at port {PORT_NUMBER}")
    daemon = threading.Thread(name='daemon_server', target=start_http_server)
    daemon.setDaemon(True)  # Set as a daemon so it will be killed once the main thread is dead.
    daemon.start()
