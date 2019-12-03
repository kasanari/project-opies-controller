import serial
import time
import json

import csv
import io

def read_IMU(connection):
    pass


def connect_to_arduino():
    try:
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=2)
    except serial.SerialException:
        ser = serial.Serial('/dev/ttyUSB1', 115200, timeout=2)
    return ser

def measure_distance(connection):
    line = b''

    while line == b'':
        msg = "a\n".encode()
        connection.write(msg)
        line = connection.readline()

    return int(line)

if __name__ == "__main__":
    a_ser = None
    try:
        a_ser = connect_to_arduino()

        for _ in range(1, 6):
            line = a_ser.readline()
            print(line)

        a_ser.write(b'a\n')

        time.sleep(5)

        while 1:
            msg = "a\n".encode()
            a_ser.write(msg)

            for i in range(0, 2):
                line = a_ser.readline().strip()
                line = line.replace(b'\x00', b'')
                line_str = line.decode()

                reader = csv.reader(
                    io.StringIO(line_str),
                    delimiter=',',
                    quotechar='"',
                    skipinitialspace=True,
                )

                for row in reader:
                    print(row)
            print("--------")

    except KeyboardInterrupt:
        print("Stopping")
        if a_ser is not None:
            a_ser.close()