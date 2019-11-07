
def _read_tlv_worker(ser):
    tlv_type_bytes = (ser.read(1))
    tlv_type = int.from_bytes(tlv_type_bytes, byteorder='big')

    length_bytes = ser.read(1)
    length = int.from_bytes(length_bytes, byteorder='big')

    value_bytes = ser.read(length)
    value = int.from_bytes(value_bytes, byteorder='big')
    return tlv_type, length, value


def read_tlv(ser, n_types=1):
    tlv_type_list = []
    tlv_length_list = []
    tlv_value_list = []

    for i in range(n_types):
        tlv_type, length, value = _read_tlv_worker(ser)
        tlv_type_list.append(tlv_type)
        tlv_length_list.append(length)
        tlv_value_list.append(value)

    return tlv_type_list, tlv_length_list, tlv_value_list
