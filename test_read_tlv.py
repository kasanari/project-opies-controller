from tlv_reader import read_tlv
import pytest


@pytest.fixture
def serial_con():
    import serial

    ser = serial.Serial(port='/dev/serial0', baudrate=115200, timeout=1)
    yield ser
    ser.close()


def test_baddr(serial_con):
    serial_con.write(b'\x10\x00')
    type_tlv, length, value = read_tlv(serial_con, n_types=2)

    assert type_tlv[0] == 64  # 0x40
    assert type_tlv[1] == 95
    assert length[0] == 1
    assert length[1] == 6
    assert value[0] == 0
    print(value[1])

