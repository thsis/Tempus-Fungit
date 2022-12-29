import logging
import signal
import random
import threading

import pandas as pd
from datetime import datetime
from colorama import Fore, Style
from utilities import get_abs_path, CONFIG, interrupt_handler, get_logger, LOG_LEVELS
from components import Relay, Controller, setup_sensors, SensorArray, PINS, write_readings


def random_time_estimator(var, target, increases=True, margin=0.1, unit="seconds", file_name=None):
    assert 0 < margin < 1, "`margin` must lie in (0, 1)."
    current_value = SENSOR_ARRAY.read(var)
    logging.debug(f"current value: {Fore.YELLOW}{current_value:.2f}{Style.RESET_ALL}.")
    logging.debug(f"turning on the connected device {'increases' if increases else 'decreases'} {var}.")
    lower = (1 - margin) * target
    upper = (1 + margin) * target

    # turn device on, if the device increases the environmental variable and current value is below lower bound
    if increases and current_value < lower:
        logging.debug(f"current value ({Fore.YELLOW}{current_value:.2f}{Style.RESET_ALL})" 
                      f" is smaller than lower limit {lower:.2f}.")
        on = True
        t = random.randint(0, 100)
    # turn device on, if the device decreases the environmental variable and current value is above upper bound
    elif not increases and current_value > upper:
        logging.debug(f"current value ({Fore.YELLOW}{current_value:.2f}{Style.RESET_ALL})" 
                      f" is larger than upper limit {upper:.2f}.")
        on = True
        t = random.randint(0, 100)
    # otherwise keep device off
    else:
        logging.debug(f"current value: {Fore.YELLOW}{current_value:.2f}{Style.RESET_ALL}, "
                      f"lower: {lower:.2f}, upper: {upper:.2f}.")
        on = False
        t = 0

    if file_name is not None:
        row = pd.Series([datetime.now(), var, current_value, on, t],
                        index=["taken_at", "variable", "value", "is_relay_on", "time_relay_on"])
        write_readings(row.to_frame().T, file_name)

    logging.debug(f"keep device on: {on}.")
    logging.debug(f"time to keep device on: {t} {unit}.")
    return on, t * SECONDS_IN_MINUTE if unit == "minutes" else t


def _convert_time_argument(x, unit):
    return x * SECONDS_IN_MINUTE if unit == "minutes" else x


def control_environment(var, relays, active_low,
                        increases,
                        target,
                        margin,
                        delay,
                        active_min,
                        active_max,
                        unit,
                        file_name):
    logging.info(f"start controlling {var}")
    logging.info(f"try to keep at {target} +/- {margin * 100:.2f}%.")
    logging.info(f"estimation strategy for turning on the device is random: " 
                 f"device may turn on for {active_min} to {active_max} {unit}")

    relays = [Relay(pin, active_low=active_low) for pin in relays]
    controller = Controller(relays,
                            active_min=_convert_time_argument(active_min, unit),
                            active_max=_convert_time_argument(active_max, unit),
                            delay=_convert_time_argument(delay, unit))
    controller.run(estimation_strategy=random_time_estimator,
                   var=var,
                   target=target,
                   increases=increases,
                   margin=margin,
                   unit=unit,
                   file_name=get_abs_path("data", file_name))


def read_all_sensors():
    SENSOR_ARRAY.read_all()


def main():
    read_sensor_thread = threading.Thread(target=read_all_sensors,
                                          name="ENV-tracker",
                                          daemon=True)
    # environmental controls, create new thread here if you want to add another controller
    control_co2_thread = threading.Thread(target=control_environment,
                                          kwargs=CO2_CONFIG,
                                          name="CO2-controller",
                                          daemon=True)
    control_humidity_thread = threading.Thread(target=control_environment,
                                               kwargs=HUMIDITY_CONFIG,
                                               name="Humidity-Controller",
                                               daemon=True)

    read_sensor_thread.start()
    control_co2_thread.start()
    control_humidity_thread.start()
    read_sensor_thread.join()


if __name__ == "__main__":
    LOG_PATH = get_abs_path("logs", "main.log")
    LOGGER = get_logger(LOG_LEVELS["debug"], LOG_PATH,
                        fmt="%(asctime)s [%(levelname)s] [%(threadName)s] [%(funcName)s] %(message)s")

    SECONDS_IN_MINUTE = 60
    SENSORS = setup_sensors(CONFIG)

    SENSOR_ARRAY = SensorArray(SENSORS,
                               out_path=get_abs_path("data", CONFIG.get("GENERAL", "env_data_file_name")),
                               retries=CONFIG.getint("SENSORS", "retries"),
                               delay=CONFIG.getint("SENSORS", "delay"))
    CO2_CONFIG = CONFIG.get_controller_config("CONTROLLER_CO2")
    HUMIDITY_CONFIG = CONFIG.get_controller_config("CONTROLLER_HUMIDITY")

    signal.signal(signal.SIGINT, interrupt_handler)
    main()
