
class TLV:
    def __init__(self, tlv_type, tlv_length, tlv_value):
        self.tlv_type = tlv_type
        self.tlv_length = tlv_length
        self.tlv_value = tlv_value

    def update(self, tlv_type, tlv_length, tlv_value):
        self.tlv_type = tlv_type
        self.tlv_length = tlv_length
        self.tlv_value = tlv_value

