import RPi.GPIO as GPIO
import time

channel = 21

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT, initial=GPIO.HIGH)


def motor_on(pin):
    GPIO.output(pin, GPIO.LOW)  # Turn motor on


def motor_off(pin):
    GPIO.output(pin, GPIO.HIGH)  # Turn motor off


if __name__ == '__main__':
    input("Start?:")
    try:
        motor_on(channel)
        time.sleep(5)
        motor_off(channel)
        GPIO.cleanup()
    except KeyboardInterrupt:
        GPIO.cleanup()