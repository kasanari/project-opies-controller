import serial
import time

try:
    ser = serial.Serial(port='/dev/tty.usbmodem0007600866181', baudrate=115200, timeout=0.5)
except RuntimeError:
    ser = serial.Serial(port='/dev/tty.usbmodem0007600866181', baudrate=115200, timeout=0.5)

ser.write(b'\r\r')  # Enter key twice to enter shell mode

res = ser.read(10)  # Read 10 bytes
time.sleep(0.5)
ser.write(b'si\r')  # System information pls
time.sleep(0.5)
# ser.write(b'acts 0 1 0 1 0 1 1 2 0\r')

f = open("location_data.txt", "w+")

print(res)
ser.write(b'lep\r')
for i in range(100):
    print('hh')
    res = ser.read(100)
    if len(res) > 0:
        res_decoded = res.decode("utf-8")
        print(res_decoded)
        # Regular expression. only write those that match POS
        f.write(res_decoded)

f.close()
