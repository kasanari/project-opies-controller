from tlv_handler import tlv_handler


def test_tlv_handler():
    tlv_type, tlv_length, tlv_value = tlv_handler("dwm_baddr_get")

    assert tlv_type[0] == 64
    assert tlv_type[1] == 95
    assert tlv_length[0] == 1
    assert tlv_length[1] == 6
    assert tlv_value[0] == 0
    print(tlv_value[1])