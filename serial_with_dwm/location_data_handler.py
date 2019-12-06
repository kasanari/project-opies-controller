from dataclasses import dataclass, asdict

@dataclass
class Transform:
    x: float
    y: float
    z: float

@dataclass
class LocationData:
    x: float  # float?
    y: float
    z: float
    quality: float

    def get_as_dict(self):
        return asdict(self)


@dataclass
class Anchor:
    anchor_id: str  # could add = '' but have to rearrange order or do to all
    position: LocationData(-99.0, -99.0, -99.0, -99.0)
    distance: float
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


def extract_location(tlv_response, n=1, max_index=13):
    list_starts_at_zero_offset = 1
    max_index = max_index - list_starts_at_zero_offset
    quality = tlv_response[n].tlv_value[max_index]  # 13 bytes, little endian. quality is at index = 12
    actualquality = 100-value_in_float(quality)  # decawave gives us an inverted quality..
    # initialize y, x, z
    z = tlv_response[n].tlv_value[max_index-1]
    y = tlv_response[n].tlv_value[max_index-5]
    x = tlv_response[n].tlv_value[max_index-9]

    for i in range(max_index-2, max_index-5, -1):
        z = z + tlv_response[n].tlv_value[i]  # concatenates the string of hexadecimal numbers
        y = y + tlv_response[n].tlv_value[i-4]
        x = x + tlv_response[n].tlv_value[i-8]

    c = LocationData(value_in_float(x, millimeter_to_meter=1), value_in_float(y, millimeter_to_meter=1),
                     value_in_float(z, millimeter_to_meter=1), actualquality)

    return c

#####
# value_in_float: converts a string written of hexadecimal values to a float number
#
# input: a string, a 0 or 1 depending on if the value should be divided by 1000.0 to get [m] instead of [mm]


def value_in_float(string, millimeter_to_meter=0):
    converted_to_byte = bytearray.fromhex(string)
    converted_to_int = int.from_bytes(converted_to_byte, byteorder='big', signed=True)  # i think i do unnecessary \
    # conversions earlier in the code..
    if millimeter_to_meter:
        to_float_divider = 1000.0
    else:
        to_float_divider = 1.0

    converted_to_float = converted_to_int/to_float_divider

    return converted_to_float
######
# extract_distances: reads bytes from value list (from tlv response) in reverse order as the values are described in
# little endian order. The first byte in the value field described the number of anchors we are reading distances from,
# then for each anchor there are 20 bytes of data. The first two bytes (first two items in the list) are the UWB ID of
# the anchor, the next 4 bytes is distance from tag to anchor, the next 13 bytes is the position of the anchor.
#
# input: list of tlv objects, index of tlv object list where the position data is in, the index the position bytes
#          start at
# output: LocationData object (dataclass)

# split into frames so I don't need dynamic offsets?


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
        start_index_bytetrain = 1+(anchor_frame_length*i)
        end_index_bytetrain = start_index_bytetrain + anchor_frame_length

        # UWB address for anchor i
        anchor_id = tlv_response[2].tlv_value[i*anchor_frame_length + uwb_address_offset + 1]
        anchor_id = anchor_id + tlv_response[2].tlv_value[i*anchor_frame_length + uwb_address_offset]

        # distance
        distance = ''
        for j in range(distance_upper_offset, distance_lower_offset-1, -1):
            distance = distance + tlv_response[2].tlv_value[j + start_index_bytetrain]

        distance_quality = tlv_response[2].tlv_value[i*anchor_frame_length+quality_offset]
        position_of_anchor_i = extract_location(tlv_response, 2, end_index_bytetrain)  # 2 is for tlv_response[2], position anchor

        a = Anchor(anchor_id, position_of_anchor_i, value_in_float(distance, millimeter_to_meter=1),
                   value_in_float(distance_quality))
        anchor_list.append(a)
    return anchor_list


