import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)


class Relay:
    def __init__(self, gpio):
        self.gpio = gpio
        self.status = "DISARMED"


if __name__ == "__main__":
    import time
    RELAY_PIN = 21
    GPIO.setup(RELAY_PIN, GPIO.OUT)
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(5)
    GPIO.output(RELAY_PIN, GPIO.LOW)