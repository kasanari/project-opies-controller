import serial
from tlv_handler import TLVHandler

API_dictionary = {
    "get_location": "dwm_loc_get",
    "get_bluetooth_info": "dwm_baddr_get",
    "get_system_info": "dwm_cfg_get",
    "get_nodeid": "dwm_nodeid_get"
}


def connect_serial_uart(command="dwm_loc_get"):
    try:
        serial_con = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=1)
        return serial_request(serial_con, command)
    except serial.SerialException:
        print("The device could not be found/no serial connection was made.")
    except KeyboardInterrupt:
        print("Closing.")
    finally:
        serial_con.close()


def get_location():
    responses, indexes = connect_serial_uart()
    if responses[0].tlv_value != 0:
        print("Error in reading location. Is the RTLS on?")
    # else:
    #     print("Location data:\n")
    return responses


def get_nodeid():
    responses, indexes = connect_serial_uart("dwm_nodeid_get")
    return responses


def serial_request(serial_con, command):
    tlv_h = TLVHandler(serial_con, command)
    tlv_h.send_tlv_request()
    tlv_object_list, indexes = tlv_h.read_tlv()

    return tlv_object_list, indexes
