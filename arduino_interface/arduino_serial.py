import serial
import asyncio


async def distance_measure_task():
    while True:
        distance = await distance_measure()
        print(f"Distance in CM: {distance}")


async def distance_measure():
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2)
    except:
        ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=2)

    ser.write(b'a')
    while True:
        line = ser.readline()
        if line != '':
            break
    distance = int(line)

    ser.close()
    return distance


if __name__ == "__main__":

    asyncio.run(distance_measure_task())