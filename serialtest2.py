import serial
import time

try:
    # mac:
    # ser = serial.Serial(port='/dev/tty.usbmodem0007600866181', baudrate=115200, timeout=0.5)
    # pi:
    ser = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=0.5)
except RuntimeError:
    # ser = serial.Serial(port='/dev/tty.usbmodem0007600866181', baudrate=115200, timeout=0.5)
    ser = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=0.5)

# ser.write(b'\r\r')  # Enter key twice to enter shell mode

# ser.write(b'')
#
f = open("location_data.txt", "w+")
# while True:
ser.write(b'\x02\x00')
for i in range(100):
    # ser.write(b'\x02\x00')
    time.sleep(0.5)
    # ser.write(b'\x15\x00')
    res = ser.read(100)  # Read 10 bytes
    res_decoded = res.decode("utf-8")

    print(res_decoded)  # reg ex för att parse:a
    f.write(res_decoded)
f.close()

# ser.write(b'si\r')  # System information pls
# time.sleep(0.5)
# # ser.write(b'acts 0 1 0 1 0 1 1 2 0\r')
#
# f = open("location_data.txt", "w+")
#
# ser.write(b'lep\r')
# for i in range(100):
# print('hh')
#  res = ser.read(100)
#   if len(res) > 0:
#        res_decoded = res.decode("utf-8")
#         print(res_decoded)
#         # Regular expression. only write those that match POS
#          f.write(res_decoded)
#
#   f.close()
