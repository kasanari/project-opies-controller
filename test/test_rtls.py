def test_create_dict():
    import rtls
    import dataclasses
    p = rtls.LocationData(10, 20, 30)
    assert p.get_as_dict() == {'x': 10, 'y': 20, 'z': 30}

