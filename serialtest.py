import serial


with serial.Serial('/dev/tty.usbmodem0007600866261', timeout=3) as ser:

    # ser = serial.Serial('/dev/tty.usbmodem0007600866261')tty.usbmodem0007600866261

    print(ser.name)
    ser.write(b'\n')
    ser.write(b'\n')
    # ser.write(bytes('hoo', encoding='ascii'))
    # ser.write(bytes('\1a', encoding='ascii'))
    # ser.write(bytes('\1a', encoding='ascii'))
    while 1:
        print('hello')
        ser.write(b'les\n')
        print('why')
        line = ser.readline()
        print('is')
        print(line.decode("utf-8"))

ser.close()
