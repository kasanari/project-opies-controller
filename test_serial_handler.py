import pytest
import serial_handler


def test_get_location():
    c = serial_handler.get_location()

    assert c[0].tlv_type == 64
    #assert int.from_bytes(c[0].tlv_value[0], byteorder='big') != 0
    assert c[1].tlv_type == 65
    assert c[1].tlv_length == 13
    assert c[2].tlv_type == 73
    # assert c[2].tlv_length == 81  1 + (20 bytes per anchor)


def test_get_nodeid():
    c = serial_handler.get_nodeid()

    assert c[0].tlv_type == 64
    #assert int.from_bytes(c[0].tlv_value[0], byteorder='big') != 0  <- conversion non-valid
