from tlv_handler import read_tlv
import pytest


@pytest.fixture
def serial_con():
    import serial

    ser = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=1)
    yield ser
    ser.close()


def test_baddr(serial_con):
    serial_con.write(b'\x10\x00')
    type_tlv, length = read_tlv(serial_con, 2)
    assert type_tlv == 64  # 0x40
    assert length == 1

