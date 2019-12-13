from serial_with_dwm.location_data_handler import extract_location, extract_distances
from serial_with_dwm.tlv_handler import TLVHandler


class SerialHandler:
    def __init__(self, ser_con):
        self.ser_con = ser_con
        self.no_response_in_a_row_count = 0

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

    def get_anchors(self, anchor_list): #process anchor_list. but what format suits the webtask?
        anchor_positions = []
        for anchor in anchor_list:
            anchor_positions.append(anchor.position)
        return anchor_positions # returns list of the anchors' positions. Maybe we want the ID:s too?
        # in that case maybe this function is unecessary - a_list in get_anchor_distances has the ID, and the LocData object
        
    def serial_request(self, command):
        tlv_h = TLVHandler(self.ser_con, command)
        tlv_h.send_tlv_request()
        tlv_object_list, indexes = tlv_h.read_tlv()

        return tlv_object_list, indexes

    def get_location_data(self):
        responses, indexes = self.serial_request("dwm_loc_get")
        if responses[0].tlv_type == 0:
            self.no_response_in_a_row_count += 1  # start keeping track of how many
            return None  # null object
        else:
            location = extract_location(responses)
            self.no_response_in_a_row_count = 0
            return location

    def get_nodeid(self):
        responses, indexes = self.serial_request("dwm_nodeid_get")
        return responses
