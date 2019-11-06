import location_server
from motor_control import Steering, Motor
import json
import asyncio

#steering = Steering(17, 4, 13)

async def motor_control_task(queue):
    steering = Steering(17, 4, 13)
    #drive = Motor(2)

    try:
        while True:
            message = await queue.get()
            message = json.loads(message)
            print(message)
            angle = float(message["angle"])
            steering.set_angle(angle)

    except asyncio.CancelledError:
        print("Motor task cancelled")
    finally:
        steering.stop()
        #drive.stop()


async def order(message):
    message = json.loads(message)
    print(message)
    angle = float(message["angle"])
    print(angle)
    #steering.set_angle(angle)

if __name__== "__main__":

    try:
        location_server.start_web_client()
        start_server = location_server.start_websocket_server()
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

    except KeyboardInterrupt:
        asyncio.get_event_loop().stop()
        print("Stopping..")