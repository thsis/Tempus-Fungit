import logging
import time
from logdecorator import log_on_start, log_on_end, log_exception
from components import Relay
from utilities import EXIT_EVENT

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self,
                 relays: list,
                 active_min: float,
                 active_max: float,
                 delay: float):
        self.relays = relays
        self.active_min = active_min
        self.active_max = active_max
        self.delay = delay

    def __sanitize(self, t):
        # handle t larger than maximum value
        if t > self.active_max:
            logger.debug(f"received {t} seconds --> truncating input to {self.active_max}.")
            return self.active_max

        # handle t smaller than min value
        if t < self.active_min:
            logger.debug(f"received {t} seconds --> truncating input to {self.active_min}.")
            return self.active_min

        if self.active_min <= t <= self.active_max:
            logger.debug(f"received {t} seconds --> passing input through.")
            return t

    def activate_relay(self, seconds):
        if seconds:
            for relay in self.relays:
                logger.debug(f"start {relay} for {seconds} seconds.")
            for relay in self.relays:
                relay.arm()
            time.sleep(seconds)
            for relay in self.relays:
                relay.disarm()

    def skip(self):
        for relay in self.relays:
            relay.disarm()

        logger.debug(f"skip this round ({self.delay} seconds).")
        time.sleep(self.delay)

    @log_on_start(logging.INFO, "start run.")
    @log_on_end(logging.INFO, "end of run.")
    @log_exception("encountered error:")
    def run(self, estimation_strategy, **kwargs):
        while True:
            if EXIT_EVENT.is_set():
                break
            try:
                turn_on, active_time = estimation_strategy(**kwargs)
                active_time = self.__sanitize(active_time)
                if turn_on:
                    self.activate_relay(active_time)
                else:
                    self.skip()

            except StopIteration:
                break


if __name__ == "__main__":
    import signal
    from components import BH1750
    from utilities import CONFIG, get_abs_path, interrupt_handler, get_logger


    def main():
        def random_lux_estimator():
            bh1750 = BH1750(address=int(CONFIG.get("SENSORS", "address_bh1750"), base=16),
                            site=CONFIG.get("GENERAL", "site"))
            current_lux = bh1750.read("light_intensity")
            logging.debug(f"currently: {current_lux} lux.")
            if current_lux >= 100:
                on = True
                t = 2
                logging.debug(f"send command to turn on sensor for {t} seconds.")
            else:
                on = False
                t = 0
                logging.debug(f"send command to turn sensor off.")
            return on, t

        relay = Relay(21)
        controller = Controller([relay], active_min=1, active_max=3, delay=2)
        controller.run(estimation_strategy=random_lux_estimator)

    rootLogger = get_logger(logging.DEBUG, get_abs_path("logs", "controller_demo.log"))

    rootLogger.debug("Debug logging test...")
    signal.signal(signal.SIGINT, interrupt_handler)
    main()


