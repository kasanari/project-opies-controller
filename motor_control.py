import RPi.GPIO as GPIO

PWM_NEUTRAL = 7.5

class Servo:
    def __init__(self, pin):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(PWM_NEUTRAL)

    def stop(self):
        self.pwm.stop()
        GPIO.cleanup()

class Steering(Servo):

    def set_angle(self, angle):
        self.pwm.ChangeDutyCycle(angle)  # TODO make this more sophisticated


class Motor(Servo):

    def neutral(self):
        self.pwm.ChangeDutyCycle(PWM_NEUTRAL)  # TODO make this more sophisticated

    def set_speed(self, speed):
        self.pwm.ChangeDutyCycle(speed)
