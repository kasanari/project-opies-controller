import RPi.GPIO as GPIO
import warnings


class Servo:
    def __init__(self, pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)

    def stop(self):
        self.pwm.stop()
        GPIO.cleanup()

class Steering(Servo):

    def __init__(self, pin, min_angle, max_angle):
        super().__init__(pin)
        self.max_angle = max_angle
        self.min_angle = min_angle
        self.neutral = (max_angle+min_angle)/2
        self.pwm.start(self.neutral)


    def set_angle(self, angle):
        if angle > self.max_angle:
            warnings.warn(f"Angle of {angle} exceeds max_angle of {self.max_angle}!")
            angle = self.max_angle
        elif angle < self.min_angle:
            warnings.warn(f"Angle of {angle} is under min_angle of {self.min_angle}!")
            angle = self.min_angle
        self.pwm.ChangeDutyCycle(angle)  # TODO make this more sophisticated


class Motor(Servo):

    def neutral(self):
        self.pwm.ChangeDutyCycle(90)  # TODO make this more sophisticated

    def set_speed(self, speed):
        self.pwm.ChangeDutyCycle(speed)
