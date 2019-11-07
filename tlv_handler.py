
def read_tlv(ser, n_types):
    type_tlv = (ser.read(1))
    type_int = int.from_bytes(type_tlv, byteorder='big')
    length_bytes = ser.read(1)
    length = int.from_bytes(length_bytes, byteorder='big')
    return type_int, length
