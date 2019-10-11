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

print(res)

while True:
    ser.write(b'help\r')
    res = ser.read(100)
    if len(res) > 0:
        print(res.decode("utf-8"))
