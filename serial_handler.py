import serial
import time
from tlv_handler import TLVHandler
from location_data_handler import extract_location, extract_distances, Anchor

# just incorporate into the functions, rm dictionary after
API_dictionary = {
    "get_location": "dwm_loc_get",
    "get_bluetooth_info": "dwm_baddr_get",
    "get_system_info": "dwm_cfg_get",
    "get_nodeid": "dwm_nodeid_get"
}


def connect_serial_uart(command="dwm_loc_get"):  # move to highest instance 'main'?
    try:
        serial_con = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=1)
        return serial_request(serial_con, command)
    except serial.SerialException:
        print("The device could not be found/no serial connection was made.")
    except KeyboardInterrupt:
        print("Hey you caught me")
    finally:
        serial_con.close()


def get_location():
    responses, indexes = connect_serial_uart()
    if responses[0].tlv_value != 0:
        print("Error in reading location. Is the RTLS on?")
        # do something clever to not crash the program?
    else:
        print("Location data:\n")
        extract_location(responses)
        # ask for locationdata from locationdata_handler. send responses. locationdata_handler
        # either sends back distances or a location
    return responses  # can get errors if minicom:ed earlier..?


def get_anchor_distances():
    responses, indexes = connect_serial_uart("dwm_loc_get")
    if responses[0].tlv_type == 0:
        print("Error in reading location. No response. Is the RTLS on?")
        return Anchor('', '', '', -1)  # empty anchor
    else:
        a_list = extract_distances(responses)
        return a_list


def get_nodeid():
    responses, indexes = connect_serial_uart("dwm_nodeid_get")
    return responses


def serial_request(serial_con, command):
    tlv_h = TLVHandler(serial_con, command)
    tlv_h.send_tlv_request()
    tlv_object_list, indexes = tlv_h.read_tlv()

    return tlv_object_list, indexes


if __name__ == "__main__":
    try:
        while True:
            a_list = get_anchor_distances()

            # specifikt till set up Pomodoro + Basilico
            if a_list[0].anchor_id == '561d':
                print("Pomodoro active")
            if a_list[1].anchor_id == '549b':
                print("Basilico acknowledged")

            distance_pomodoro = int(a_list[0].distance, base=16)
            print("Pomodoro:")
            print(distance_pomodoro)
            distance_basilico = int(a_list[1].distance, base=16)
            print("Basilico:")
            print(distance_basilico)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopping..")
