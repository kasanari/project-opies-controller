import serial
import sys
from tlv_reader import read_tlv
from tlv_sender import send_tlv


def tlv_handler(tlv_command):
    try:
        ser = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=1)
        command = API_dictionary.get(tlv_command)
        command_byte_sequence = command[0]
        command_n_responses = command[1]

        send_tlv(ser, command_byte_sequence)
        tlv_type, tlv_length, tlv_value = read_tlv(ser, command_n_responses)

        return tlv_type, tlv_length, tlv_value

    except serial.SerialException:
        print("The device could not be found/no serial connection was made.")
        sys.exit()

    except KeyboardInterrupt:
        print("Closing.")

    finally:
        ser.close()


API_dictionary = {
  "dwm_loc_get": [b'\x0c\x00', 3],
  "dwm_baddr_get": [b'\x10\x00', 2]
}
