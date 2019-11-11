import RPi.GPIO as GPIO
import warnings

def cleanup():
    GPIO.cleanup()

def rescale(x, min, max):
    return min + x*(max - min)

class Servo:
    def __init__(self, pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)
        self.neutral = 7.5

    def stop(self):
        self.pwm.stop()


class Steering(Servo):

    def __init__(self, pin, min_angle, max_angle):
        super().__init__(pin)
        self.max_angle = max_angle
        self.min_angle = min_angle
        self.pwm.start(self.neutral)


    def set_angle(self, angle):

        angle = rescale(angle, self.min_angle, self.max_angle)

        if angle > self.max_angle:
            warnings.warn(f"Angle of {angle} exceeds max_angle of {self.max_angle}!")
            angle = self.max_angle
        elif angle < self.min_angle:
            warnings.warn(f"Angle of {angle} is under min_angle of {self.min_angle}!")
            angle = self.min_angle
        print(f"Wheel angle changed to {angle}.")
        self.pwm.ChangeDutyCycle(angle)


class Motor(Servo):

    def __init__(self, pin, max_back_speed=7, max_forward_speed=8):
        super().__init__(pin)
        self.pwm.start(self.neutral)
        self.max_fspeed = max_forward_speed
        self.max_bspeed = max_back_speed

    def neutral(self):
        self.pwm.ChangeDutyCycle(7.5)

    def set_speed(self, speed):

        speed = rescale(speed, self.max_bspeed, self.max_fspeed)

        if speed > self.max_fspeed:
            speed = self.max_fspeed
            warnings.warn(f"{speed} exceeds max speed of {self.max_fspeed}!")
        elif speed < self.max_bspeed:
            speed = self.max_bspeed
            warnings.warn(f"{speed} is under min_angle of {self.max_bspeed}!")
        print(f"Speed changed to {speed}.")
        self.pwm.ChangeDutyCycle(speed)
