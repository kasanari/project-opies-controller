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
    anchor_id: str
    position: LocationData()
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
        c.z = c.z + tlv_response[n].tlv_value[i]  # concatenate? (might have to make it into a string)
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
    c = Anchor()
    # initialize y, x, z

    # WIP under here
    c.z = tlv_response[3].tlv_value[11]
    c.y = tlv_response[3].tlv_value[7]
    c.x = tlv_response[3].tlv_value[3]

    for i in range(10, 8, -1):
        c.z = c.z + tlv_response.tlv_value[i]  # concatenate? (might have to make it into a string)
        c.y = c.y + tlv_response.tlv_value[i - 4]
        c.x = c.x + tlv_response.tlv_value[i - 8]

    return c


