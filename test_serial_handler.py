import pytest
import serial_handler


def test_get_location():
    c = serial_handler.get_location()

    assert c[0].tlv_value != -1
