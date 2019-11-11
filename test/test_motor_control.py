from motor_control import Steering
import time


def test_steering():
    steering = Steering(17)

    try:
        while True:
            # angle = input("Set angle: ")
            steering.set_angle(int(4))
            time.sleep(2)
            steering.set_angle(int(13))
            time.sleep(2)
    except KeyboardInterrupt:
        steering.stop()
        print("Stopping...")
