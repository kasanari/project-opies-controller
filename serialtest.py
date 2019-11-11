import serial
from time import sleep


def encode(type_1, length, value):
    return chr(type_1) + chr(length) + value


with serial.Serial('/dev/tty.usbmodem0007600866181', timeout=3) as ser:
    # ser = serial.Serial('/dev/tty.usbmodem0007600866261')tty.usbmodem0007600866261
    # tlv = TLV(['84', 'A5'])  # provide the possible tag values
    # print(tlv.parse('840E315041592E5359532E4444463031A5088801025F2D02656E'))
    # tlv = TLV(['9F02', '9F04'])
    # tlv.build({'9f02': '000000001337'})

    print(ser.name)
    ser.write(0x0D)  # enter
    sleep(0.2)
    ser.write(0x0D)  # enter
    sleep(0.1)

    c = ser.read(10)

    ser.write(0x73)
    ser.write(0x69)
    # ser.write(0x6C)  # l
    # ser.write(0x65)  # e
    # ser.write(0x63)  # c
    ser.write(0x0D)  # enter
    # ser.write(0x0B)
    # ser.write(b'\r')
    # sleep(0.2)
    # ser.write(b'\r')
    # ser.write(0x01)
    # ser.write(0x01)  # write a string
    # sleep(0.2)
    # ser.write(b'\r')  # write a string
    # sleep(1)

    # ser.write(b'0x15')
    # ser.write(b'0x00')
    # ser.write(b'\n')
    # ser.write(bytes('hoo', encoding='ascii'))
    # ser.write(bytes('\1a', encoding='ascii'))
    # ser.write(bytes('\1a', encoding='ascii'))
    while 1:
        print('hello')
        #    ser.write(b'les\n')
        #    print('why')
        line = ser.readline()
        #    print('is')
        print(line.decode("utf-8"))

ser.close()
