import serial
import sys
from TLV import TLV


class TLVHandler:
    def __init__(self, ser, tlv_command):
        self.ser = ser
        self.tlv_command = tlv_command  # TODO does command need to be saved? muse on it.
        self.tlv_bytes, self.tlv_n_responses = API_dictionary.get(self.tlv_command)

    def send_tlv_request(self):
        send_tlv(self.ser, self.tlv_bytes)

    def read_tlv(self):
        tlv_object_list = read_tlv(self.ser, self.tlv_n_responses)
        return tlv_object_list, self.tlv_n_responses  # self.tlv_n_responses is length of list!


####################################
# Functions
####################################

# _read_tlv_worker: reads TLV responses
# input: serial connection
# output: a TLV object with read bytes
def _read_tlv_worker(ser):
    tlv_type_bytes = (ser.read(1))
    tlv_type = int.from_bytes(tlv_type_bytes, byteorder='big')

    length_bytes = ser.read(1)
    length = int.from_bytes(length_bytes, byteorder='big')

    value = []
    for i in range(length):
        value_bytes = ser.read(1)
        value.append(value_bytes.hex())

    c = TLV(tlv_type, length, value)
    return c


# read_tlv: calls to _read_tlv_worker to read a number of tlv response(s)
# input: serial connection, number of tlv responses expected from send request
# output: list of TLV objects
def read_tlv(ser, n_types=1):
    tlv_list = []

    for i in range(n_types):
        tlv_list.append(_read_tlv_worker(ser))

    return tlv_list


# send_tlv: sends a tlv request
# input: serial connection, hexadecimal codes of bytes to send
# output: none
def send_tlv(ser, send_bytes):
    ser.write(send_bytes)


def distance_to_anchor(self):
    pass  # in loop from range(tlv.value[0] in the .tlv_value list on tlv_list[2],
    # skip 1 + 2 + (n-1)*18  entries to then read the following 4 bytes for distance to anchor n. 5th byte is quality


API_dictionary = {
    "dwm_loc_get": [b'\x0c\x00', 3],  # position value: from output value in 2nd response type
    "dwm_baddr_get": [b'\x10\x00', 2],
    "dwm_cfg_get": [b'\x08\x00', 2],
    "dwm_nodeid_get": [b'\x30\x00', 2]
}
