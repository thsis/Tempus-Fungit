import logging
import signal
import random
import threading

import pandas as pd
from datetime import datetime
from colorama import Fore, Style
from utilities import get_abs_path, CONFIG, interrupt_handler, get_logger, LOG_LEVELS
from components import Relay, Controller, setup_sensors, SensorArray, write_readings


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
    return on, _convert_time_argument(t, unit)


def constant_time_estimator(var, active_min, active_max, delay, unit="hours", file_name=None, **kwargs):
    now = datetime.now()
    now_hour = now.hour
    on = active_min <= now_hour <= active_max
    logging.debug(f"control {var}, keep lights on: {on}.")
    logging.debug(f"time to keep lights on: {delay} {unit}.")
    if file_name:
        row = pd.Series([now, on, delay], index=["taken_at", "turn_on", "duration"])
        write_readings(row.to_frame().T, file_name)
    return on, _convert_time_argument(delay, unit)


def _convert_time_argument(x, unit):
    if unit == "minutes":
        return x * SECONDS_IN_MINUTE
    elif unit == "hours":
        return x * SECONDS_IN_MINUTE * MINUTES_IN_HOUR
    else:
        return x


def control(var, relays, active_low, delay, active_min, active_max, unit, estimation_strategy,
            increases=None, target=None, margin=None, file_name=None):
    logging.info(f"start controlling {var}")
    if margin:
        logging.info(f"try to keep at {target} +/- {margin * 100:.2f}%.")

    relays = [Relay(pin, active_low=active_low) for pin in relays]
    controller = Controller(relays,
                            active_min=_convert_time_argument(active_min, unit),
                            active_max=_convert_time_argument(active_max, unit),
                            delay=_convert_time_argument(delay, unit))
    controller.run(estimation_strategy=estimation_strategy,
                   var=var,
                   target=target,
                   increases=increases,
                   margin=margin,
                   unit=unit,
                   active_min=active_min,
                   active_max=active_max,
                   delay=delay,
                   file_name=get_abs_path("data", file_name))


def read_all_sensors():
    SENSOR_ARRAY.read_all()


def make_config(section, estimation_strategy):
    kwargs = {**CONFIG.get_controller_config(section),
              "estimation_strategy": estimation_strategy}
    return kwargs


def main():
    read_sensor_thread = threading.Thread(target=read_all_sensors,
                                          name="ENV-tracker",
                                          daemon=True)
    # environmental controls, create new thread here if you want to add another controller
    control_co2_thread = threading.Thread(target=control,
                                          kwargs=CO2_CONFIG,
                                          name="CO2-controller",
                                          daemon=True)
    control_humidity_thread = threading.Thread(target=control,
                                               kwargs=HUMIDITY_CONFIG,
                                               name="Humidity-Controller",
                                               daemon=True)

    control_lights_thread = threading.Thread(target=control,
                                             kwargs=LIGHTS_CONFIG,
                                             name="Lights-Controller",
                                             daemon=True)

    read_sensor_thread.start()
    control_co2_thread.start()
    control_humidity_thread.start()
    control_lights_thread.start()
    read_sensor_thread.join()


if __name__ == "__main__":
    LOG_PATH = get_abs_path("logs", "main.log")
    LOGGER = get_logger(LOG_LEVELS["debug"], LOG_PATH,
                        fmt="%(asctime)s [%(levelname)s] [%(threadName)s] [%(funcName)s] %(message)s")

    SECONDS_IN_MINUTE = 60
    MINUTES_IN_HOUR = 60

    CO2_CONFIG = make_config("CONTROLLER_CO2", random_time_estimator)
    HUMIDITY_CONFIG = make_config("CONTROLLER_HUMIDITY", random_time_estimator)
    LIGHTS_CONFIG = make_config("CONTROLLER_LIGHTS", constant_time_estimator)

    SENSORS = setup_sensors(CONFIG)

    SENSOR_ARRAY = SensorArray(SENSORS,
                               out_path=get_abs_path("data", CONFIG.get("GENERAL", "env_data_file_name")),
                               retries=CONFIG.getint("SENSORS", "retries"),
                               delay=CONFIG.getint("SENSORS", "delay"))

    signal.signal(signal.SIGINT, interrupt_handler)
    main()
