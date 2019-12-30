from gpiozero import Servo, AngularServo
import asyncio
import gpiozero.pins
class Car:

    def __init__(self, offline_debug=False):

        if offline_debug:
            from gpiozero.pins.mock import MockFactory
            factory = MockFactory(pin_class=gpiozero.pins.mock.MockPWMPin)
        else:
            from gpiozero.pins.pigpio import PiGPIOFactory
            factory = PiGPIOFactory()

        self.current_direction = 0
        self.max_speed = 0.2
        self.steering_offset = -9.5
        motor_max_duty = 0.1
        motor_min_duty = 0.05
        min_pulse_width = motor_min_duty * 20/1000
        max_pulse_width = motor_max_duty * 20/1000

        self.steering_servo = AngularServo(13, pin_factory=factory, initial_angle=-9.5, min_angle=-45, max_angle=45)  # initial_value=-0.2, pin_factory=factory)
        self.motor_servo = Servo(19, pin_factory=factory, min_pulse_width=min_pulse_width, max_pulse_width=max_pulse_width)

    def stop(self):
        self.steering_servo.mid()
        self.motor_servo.mid()
        self.current_direction = 0

    def disable(self):
        self.steering_servo.detach()
        self.motor_servo.detach()

    def set_wheel_angle(self, angle):
        angle += self.steering_offset
        if angle < -34.5:
            angle = -34.5
        if angle > 17.5:
            angle = 17.5

        self.steering_servo.angle = angle

    def set_acceleration(self, speed):
        if speed < 0:
            speed = speed * 2
            self.current_direction = -1
        elif speed > 0:
            self.current_direction = 1
        else:
            self.current_direction = 0

        if speed > self.max_speed:
            speed = self.max_speed

        elif speed < -2*self.max_speed:
            speed = -2*self.max_speed

        self.motor_servo.value = speed

    async def brake(self):
        if self.current_direction > 0:
            print("Braking")
            self.motor_servo.value = -1
            await asyncio.sleep(1)
            self.motor_servo.value = 0
        else:
            self.motor_servo.value = 0
        self.current_direction = 0

    async def reverse(self):
        await self.brake()
        await asyncio.sleep(1)
        print("Waiting in neutral...")
        self.set_acceleration(0)
        await asyncio.sleep(1)
