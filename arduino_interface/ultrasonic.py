def measure_distance(connection):
    line = b''

    while line == b'':
        msg = "a\n".encode()
        connection.write(msg)
        line = connection.readline()

    return int(line)
