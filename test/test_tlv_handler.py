import pytest
from serial_with_dwm.tlv_handler import TLVHandler


@pytest.fixture
def serial_con():
    import serial

    ser = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=1)
    yield ser
    ser.close()


def test_baddr_get(serial_con):
    tlvh1 = TLVHandler(serial_con, "dwm_baddr_get")
    tlvh1.send_tlv_request()
    tlv_object_list, indexes = tlvh1.read_tlv()

    assert indexes == 2
    assert tlv_object_list[0].tlv_type == 64
    assert tlv_object_list[1].tlv_type == 95
    assert tlv_object_list[0].tlv_length == 1
    assert tlv_object_list[1].tlv_length == 6
    assert tlv_object_list[0].tlv_value == 0
    print(tlv_object_list[1].tlv_value)
