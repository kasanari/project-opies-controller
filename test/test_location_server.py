def test_start_server():
    import location_server
    location_server.run(handler_class=location_server.RequestHandler)
    return True

