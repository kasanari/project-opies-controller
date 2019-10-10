from rtls import Tag


class Car:

    def __init__(self):
        self.stopped = True
        self.tag = Tag(1, 1, 1, 1)  # TODO get initial position

    def drive_to_point(self, x, y):
        # TODO implement this
        pass

    def stop(self):
        # TODO stop motors
        self.stopped = True

    def turn_wheels(self, degrees):
        # TODO turn wheels x degrees
        pass

    def set_velocity(self, speed, direction):
        # TODO set motor speed and direction
        pass
