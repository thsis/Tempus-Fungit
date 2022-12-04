import logging
import time
from logdecorator import log_on_start, log_on_end, log_exception
from components import Relay

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self,
                 relay: Relay,
                 active_min: float,
                 active_max: float,
                 delay: float):
        self.relay = relay
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
            logger.debug(f"start {self.relay} for {seconds} seconds.")
            self.relay.arm()
            time.sleep(seconds)
            self.relay.disarm()

    def skip(self):
        self.relay.disarm()
        logger.debug(f"skip this round ({self.delay} seconds).")
        time.sleep(self.delay)

    @log_on_start(logging.INFO, "start run.")
    @log_on_end(logging.INFO, "end of run.")
    @log_exception("encountered error:")
    def run(self, estimation_strategy):
        estimate_active_time = estimation_strategy()
        while True:
            try:
                self.relay.disarm()
                turn_on, active_time = next(estimate_active_time)
                active_time = self.__sanitize(active_time)
                if turn_on:
                    self.activate_relay(active_time)
                else:
                    self.skip()

            except StopIteration:
                break


if __name__ == "__main__":
    import random
    import signal
    from components import BH1750
    from utilities import CONFIG, get_abs_path, interrupt_handler

    def random_lux_estimator():
        bh1750 = BH1750(address=int(CONFIG.get("SENSORS", "address_bh1750"), base=16),
                        site=CONFIG.get("GENERAL", "site"))

        while True:
            reading, = bh1750.read()
            current_lux = reading.value
            logging.debug(f"currently: {current_lux} lux.")
            if current_lux >= 100:
                on = True
                t = random.randint(1, 10)
                logging.debug(f"send command to turn on sensor for {t} seconds.")
            else:
                on = False
                t = 0
                logging.debug(f"send command to turn sensor off.")
            yield on, t


    def main():
        relay = Relay(21)
        controller = Controller(relay, active_min=3, active_max=5, delay=5)
        controller.run(estimation_strategy=random_lux_estimator)


    logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)

    fileHandler = logging.FileHandler(get_abs_path("logs", "controller_demo.log"))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    rootLogger.debug("Debug logging test...")
    signal.signal(signal.SIGINT, interrupt_handler)
    main()


