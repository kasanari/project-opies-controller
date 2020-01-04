from serial_with_dwm import LocationData


def test_create_dict():

    p = LocationData(10, 20, 30)
    assert p.get_as_dict() == {'x': 10, 'y': 20, 'z': 30}

