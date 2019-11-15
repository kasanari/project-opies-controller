import serial
import time
import asyncio
from tlv_handler import TLVHandler
from location_data_handler import extract_location, extract_distances, Anchor, LocationData


class SerialHandler:
    def __init__(self, ser_con):
        self.ser_con = ser_con

    def close_serial(self):
        self.ser_con.close()

    def get_anchor_distances(self):
        responses, indexes = self.serial_request("dwm_loc_get")
        if responses[0].tlv_type == 0:
            print("Error in reading location. No response. Is the RTLS on?")
            return []  # empty list
        else:
            a_list = extract_distances(responses)
            return a_list

    def serial_request(self, command):
        tlv_h = TLVHandler(self.ser_con, command)
        tlv_h.send_tlv_request()
        tlv_object_list, indexes = tlv_h.read_tlv()

        return tlv_object_list, indexes

    def get_location_data(self):
        responses, indexes = self.serial_request("dwm_loc_get")
        if responses[0].tlv_type == 0:
            print("Error in reading location. No response. Is the RTLS on?")
            return None  # null object
        else:
            location = extract_location(responses)
            return location

    def get_nodeid(self):
        responses, indexes = self.serial_request("dwm_nodeid_get")
        return responses


async def serial_task(to_web_queue: asyncio.Queue, to_motor_queue: asyncio.Queue):
    try:
        ser_con = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=1)
        ser_handler = SerialHandler(ser_con)
        while True:
            loc_data = ser_handler.get_location_data()
            asyncio.gather(to_web_queue.put(loc_data), to_motor_queue.put(loc_data))
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("Stopping..")
    except serial.SerialException:
        print("The device could not be found/no serial connection was made.")
    except asyncio.CancelledError:
        print("Task cancelled.")
    finally:
        if ser_con is not None:
            ser_con.close()





if __name__ == "__main__":
    try:
        serial_con = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=1)
        s = SerialHandler(serial_con)

        while True:
            anc_list = s.get_anchor_distances()

            length = len(anc_list)
            if length < 4:
                print("List length is only: ")
                print(length)
                print("We won't get a position estimate from this.")
            else:  # specifikt till set up Pomodoro - Funghi - Basilico - Tagliatelle i ordn. 1, 2, 3, 4
                #if a_list[0].anchor_id == '49af' & a_list[1].anchor_id == '549b' & a_list[2].anchor_id == '561d' \
                        #& a_list[3].anchor_id == '8a25':
                print("4 node Pizza Party is active! Let's get that position!")
                location_of_tag = s.get_location_data()
                print("Tag is at:")
                print(location_of_tag.get_as_dict())

                # distance_pomodoro = int(a_list[0].distance, base=16)
                # print("Pomodoro:")
                # print(distance_pomodoro)
                # distance_basilico = int(a_list[1].distance, base=16)
                # print("Basilico:")
                # print(distance_basilico)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopping..")
    except serial.SerialException:
        print("The device could not be found/no serial connection was made.")
    finally:
        serial_con.close()
