def dwm_posget(ser):
    ser.write(b'\x02\x00')


def dwm_locget(ser):
    ser.write(b'\x0c\x00')


def get_location(n):  # get location with x many entries
    f = open("location_data.txt", "r")
    f1 = f.readlines()
    return f1
