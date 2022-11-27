import RPi.GPIO as GPIO
from colorama import Fore, Style


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

    def get_status(self, return_signal=False):
        channel = str(self.channel).rjust(2, "0")
        if self.status:
            msg = f"Relay GPIO {self.channel}: {Fore.RED}{'[ARMED]'.rjust(11)}{Style.RESET_ALL}"
        else:
            msg = f"Relay GPIO {self.channel}: {Fore.GREEN}{'[DISARMED]'.rjust(11)}{Style.RESET_ALL}"
        if return_signal:
            return self.status, msg
        else:
            return msg

    def _set_status(self, status):
        self.status = status

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


    def interrupt_handler_with_cleanup(signum):
        interrupt_handler(signum, cleanup_func=GPIO.cleanup())

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


    signal.signal(signal.SIGINT, interrupt_handler_with_cleanup)
    main()

