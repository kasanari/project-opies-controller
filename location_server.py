#!/usr/bin/python
from http.server import HTTPServer, SimpleHTTPRequestHandler
import websockets
import threading


def start_websocket_server(ip_addr, handler_func):
    """Starts the WebSocket server"""
    print("Starting Websocket Server")
    return websockets.serve(handler_func, ip_addr, 5678)


def start_http_server(port):
    """Starts the web client http server"""
    server_address = ('', port)
    HTTPServer(server_address, SimpleHTTPRequestHandler).serve_forever()


def start_web_client(port):
    """Starts the web client as a seperate thread"""
    print(f"Starting HTTP Server at port {port}")
    daemon = threading.Thread(name='daemon_server', target=start_http_server, args=[port])
    daemon.setDaemon(True)  # Set as a daemon so it will be killed once the main thread is dead.
    daemon.start()
