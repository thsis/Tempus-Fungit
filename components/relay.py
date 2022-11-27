import RPi.GPIO as GPIO
from colorama import Fore, Style
import time

GPIO.setmode(GPIO.BCM)


class Relay:
    def __init__(self, channel, active_low=True, initial_on=False):
        self.channel = channel
        self.active_low = active_low
        self.status = initial_on

        GPIO.setup(self.channel, GPIO.OUT,
                   initial=self._get_turn_on_signal() if self.status else self._get_turn_off_signal())

    def __del__(self):
        GPIO.cleanup(self.channel)

    def _get_turn_on_signal(self):
        if self.active_low:
            return GPIO.LOW
        else:
            return GPIO.HIGH

    def _get_turn_off_signal(self):
        if self.active_low:
            return GPIO.HIGH
        else:
            return GPIO.LOW

    def get_status(self):
        if self.status:
            msg = f"Relay Status on GPIO Pin {self.channel}: {Fore.RED}[ARMED]{Style.RESET_ALL}"
        else:
            msg = f"Relay Status on GPIO Pin {self.channel}: {Fore.GREEN}[DISARMED]{Style.RESET_ALL}"
        return self.status, msg

    def _set_status(self, status):
        self.status = status

    def arm(self):
        GPIO.output(self.channel, self._get_turn_on_signal())
        self._set_status(True)

    def disarm(self):
        GPIO.output(self.channel, self._get_turn_off_signal())
        self._set_status(False)


if __name__ == '__main__':
    relay = Relay(21)
    while True:
        try:
            relay.arm()
            time.sleep(5)
            relay.disarm()
        except KeyboardInterrupt:
            relay.disarm()
            del relay
