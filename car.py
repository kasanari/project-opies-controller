from gpiozero import Servo, AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

class Car:

    def __init__(self):
        self.stopped = True

        factory = PiGPIOFactory()

        motor_max_duty = 0.1
        motor_min_duty = 0.05
        min_pulse_width = motor_min_duty * 20/1000
        max_pulse_width = motor_max_duty * 20/1000
        self.steering_servo = AngularServo(13, initial_angle=-9.5, min_angle=-45, max_angle=45)  # initial_value=-0.2, pin_factory=factory)
        self.motor_servo = Servo(19, pin_factory=factory, min_pulse_width=min_pulse_width, max_pulse_width=max_pulse_width)

    def stop(self):
        self.steering_servo.mid()
        self.motor_servo.mid()
        self.stopped = True

    def disable(self):
        self.steering_servo.detach()
        self.motor_servo.detach()

    def turn_wheels(self, degrees):
        # TODO turn wheels x degrees
        pass

    def set_velocity(self, speed, direction_backward=bool):
        # TODO set motor speed and direction
        pass
