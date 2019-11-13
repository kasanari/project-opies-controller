from dataclasses import dataclass, asdict


@dataclass
class LocationData:
    x: str
    y: str
    z: str
    quality: float

    def get_as_dict(self):
        return asdict(self)


@dataclass
class Anchor:
    anchor_id: str  # could add = '' but have to rearrange order or do to all
    position: LocationData('', '', '', -1)
    distance: str
    distance_quality: float

    def get_as_dict(self):
        return asdict(self)

####################################
# Functions
####################################

######
# extract_location: reads bytes from value list (from tlv response) in reverse order as the location
# is described in little endian. The position data is 13 bytes long. Handles the bytes as string to concatenate.
#
# input: list of tlv objects, index of tlv object list where the position data is in, the index the position bytes
#          start at
# output: LocationData object (dataclass)


def extract_location(tlv_response, n=2, max_index=13):
    c = LocationData
    list_starts_at_zero_offset = 1
    max_index = max_index - list_starts_at_zero_offset
    c.quality = tlv_response[n].tlv_value[max_index]  # 13 bytes, little endian. quality is at index = 12
    # initialize y, x, z
    c.z = tlv_response[n].tlv_value[max_index-1]
    c.y = tlv_response[n].tlv_value[max_index-5]
    c.x = tlv_response[n].tlv_value[max_index-9]

    for i in range(max_index-2, max_index-5, -1):
        c.z = c.z + tlv_response[n].tlv_value[i]  # concatenate pls? (might have to make it into a string)
        c.y = c.y + tlv_response[n].tlv_value[i-4]
        c.x = c.x + tlv_response[n].tlv_value[i-8]

    return c

######
# extract_distances: reads bytes from value list (from tlv response) in reverse order as the values are described in
# little endian order. The first byte in the value field described the number of anchors we are reading distances from,
# then for each anchor there are 20 bytes of data. The first two bytes (first two items in the list) are the UWB ID of
# the anchor, the next 4 bytes is distance from tag to anchor, the next 13 bytes is the position of the anchor.
#
# input: list of tlv objects, index of tlv object list where the position data is in, the index the position bytes
#          start at
# output: LocationData object (dataclass)


def extract_distances(tlv_response):
    anchor_list = []
    # offsets
    uwb_address_offset = 1
    distance_lower_offset = 2
    distance_upper_offset = 5
    quality_offset = 7
    anchor_frame_length = 20
    anchor_position_offset = 12

    n_anchors = int(tlv_response[2].tlv_value[0])

    for i in range(n_anchors):  # loops through anchors
        a = Anchor('', '', '', -1)
        start_index_bytetrain = 1+(anchor_frame_length*i)
        end_index_bytetrain = start_index_bytetrain + anchor_frame_length

        # UWB address for anchor i
        a.anchor_id = tlv_response[2].tlv_value[i*anchor_frame_length + uwb_address_offset + 1]
        a.anchor_id = a.anchor_id + tlv_response[2].tlv_value[i*anchor_frame_length + uwb_address_offset]

        # distance
        for j in range(distance_upper_offset, distance_lower_offset-1, -1):
            a.distance = a.distance + tlv_response[2].tlv_value[j + start_index_bytetrain]

        a.distance_quality = tlv_response[2].tlv_value[i*anchor_frame_length+quality_offset]
        a.position = extract_location(tlv_response, 2, end_index_bytetrain)  # 2 is tlv_response[2]

        anchor_list.append(a)
    return anchor_list


