import serial

def connect_to_arduino():
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=2)
    except serial.SerialException:
        ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=2)
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

        while 1:
            distance = measure_distance(a_ser)
            print(distance)

    except KeyboardInterrupt:
        print("Stopping")
        if a_ser is not None:
            a_ser.close()