import warnings
import asyncio
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

async def motor_control_task(queue):
    factory = PiGPIOFactory()

    motor_max_duty = 0.1
    motor_min_duty = 0.05
    min_pulse_width = motor_min_duty * 20/1000
    max_pulse_width = motor_max_duty * 20/1000
    steering = Servo(13, pin_factory=factory)
    motor = Servo(19, pin_factory=factory, min_pulse_width=min_pulse_width, max_pulse_width=max_pulse_width)

    print("Initialized motors.")

    try:
        while True:
            message = await queue.get()
            print(message)
            message_type = message["type"]

            if message_type == "car_control":
                try:
                    angle = float(message["angle"])
                    steering.value = angle
                except ValueError as e:
                    print(e)

                try:
                    speed = float(message["speed"])
                    motor.value = speed
                except ValueError as e:
                    print(e)
            elif message_type == "destination":
                print(f"Going to ({message['x']}, {message['y']})")
            elif message_type == 'stop':
                motor.mid()
                steering.mid()

    except asyncio.CancelledError:
        print("Motor task cancelled.")
    finally:
        steering.detach()
        motor.detach()

def rescale(x, minimum, maximum):
    return minimum + x * (maximum - minimum)


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
