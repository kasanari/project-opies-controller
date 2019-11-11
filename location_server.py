#!/usr/bin/python
from http.server import HTTPServer, SimpleHTTPRequestHandler
import websockets
import threading

PORT_NUMBER = 8080
IP = "192.168.1.251"
#IP = "192.168.0.24"

def start_websocket_server(handler_func):
    print("Starting Websocket Server")
    return websockets.serve(handler_func, IP, 5678)


def start_http_server():
    server_address = ('', PORT_NUMBER)
    HTTPServer(server_address, SimpleHTTPRequestHandler).serve_forever()


def start_web_client():
    print(f"Starting HTTP Server at port {PORT_NUMBER}")
    daemon = threading.Thread(name='daemon_server', target=start_http_server)
    daemon.setDaemon(True)  # Set as a daemon so it will be killed once the main thread is dead.
    daemon.start()
