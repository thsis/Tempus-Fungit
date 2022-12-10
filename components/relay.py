import logging
import RPi.GPIO as GPIO
from colorama import Fore, Style

logger = logging.getLogger(__name__)


class Relay:
    counter = 0

    def __init__(self, channel, active_low=True, initial_on=False):
        Relay.counter += 1
        self.channel = channel
        self.active_low = active_low
        self.status = initial_on

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.channel, GPIO.OUT,
                   initial=self._get_turn_on_signal() if self.status else self._get_turn_off_signal())

    def __str__(self):
        return f"Relay {Relay.counter}"

    def __del__(self):
        self.disarm()
        logger.debug(f"cleaning up {self.__str__()}")
        GPIO.setmode(GPIO.BCM)
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

    def get_status(self, return_signal=False):
        channel = str(self.channel).rjust(2, "0")
        if self.status:
            msg = f"GPIO {channel}: {Fore.RED}{'[ARMED]'.rjust(11)}{Style.RESET_ALL}"
        else:
            msg = f"GPIO {channel}: {Fore.GREEN}{'[DISARMED]'.rjust(11)}{Style.RESET_ALL}"
        if return_signal:
            return self.status, msg
        else:
            return msg

    def _set_status(self, status):
        self.status = status
        logger.info(f"status {self.__str__()} {self.get_status()}")

    def arm(self):
        GPIO.output(self.channel, self._get_turn_on_signal())
        self._set_status(True)

    def disarm(self):
        GPIO.output(self.channel, self._get_turn_off_signal())
        self._set_status(False)


if __name__ == '__main__':
    import time
    import signal
    from utilities import interrupt_handler


    def main():
        GPIO.setmode(GPIO.BCM)
        relay = Relay(21)
        while True:
            relay.arm()
            print(relay.get_status())
            time.sleep(5)
            relay.disarm()
            print(relay.get_status())
            time.sleep(5)


    signal.signal(signal.SIGINT, interrupt_handler)
    main()

