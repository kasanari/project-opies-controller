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


def extract_location(tlv_response, n=2, max_index=12):
    c = LocationData
    c.quality = tlv_response[n].tlv_value[max_index]  # 13 bytes, little endian. quality is at index = 12
    # initialize y, x, z
    c.z = tlv_response[n].tlv_value[max_index-1]
    c.y = tlv_response[n].tlv_value[max_index-5]
    c.x = tlv_response[n].tlv_value[max_index-9]

    for i in range(max_index-2, max_index-4, -1):
        c.z = c.z + tlv_response[n].tlv_value[i]  # concatenate pls? (might have to make it into a string)
        c.y = c.y + tlv_response[n].tlv_value[i-4]
        c.x = c.x + tlv_response[n].tlv_value[i-8]

    return c

######
# extract_distances: reads bytes from value list (from tlv response) in reverse order as the values are described in
# little endian order. The first byte in the value field described the number of anchors we are reading distances from,
# then for each tag there are 20 bytes of data. The first two bytes (first two items in the list) are the UWB ID of the
# anchor, the next 4 bytes is distance from tag to anchor, the next 13 bytes is the position of the anchor.
#
# input: list of tlv objects, index of tlv object list where the position data is in, the index the position bytes
#          start at
# output: LocationData object (dataclass)


def extract_distances(tlv_response):
    a_list = []
    # initialize y, x, z

    n_anchors = int(tlv_response[2].tlv_value[0])

    for i in range(n_anchors):  # loops through anchors
        a = Anchor('', '', '', -1)
        start_index_bytetrain = 1+(20*i)
        end_index_bytetrain = 20*(i+1)

        # UWB address for anchor i
        a.anchor_id = tlv_response[2].tlv_value[start_index_bytetrain+1]
        a.anchor_id = a.anchor_id + tlv_response[2].tlv_value[start_index_bytetrain]
        a_list.append(a)

        # distance
        for j in range(start_index_bytetrain + 6, start_index_bytetrain + 2, -1):
            a.distance = a.distance + tlv_response[2].tlv_value[j]
        a.position = extract_location(tlv_response, 2, end_index_bytetrain)
    return a_list


