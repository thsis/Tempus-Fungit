import random
import logging
import pandas as pd
from datetime import datetime
from colorama import Fore, Style
from utilities import CONFIG, LOG_LEVELS, get_abs_path
from components import DHT22, BH1750, BMP280, SCD30, write_readings, SensorArray, PINS, Relay, Controller

SENSORS = [
    DHT22(address=PINS[CONFIG.get("SENSORS", "address_dht22")], site=CONFIG.get("GENERAL", "site")),
    BH1750(address=int(CONFIG.get("SENSORS", "address_bh1750"), base=16), site=CONFIG.get("GENERAL", "site")),
    # BMP280(address=int(CONFIG.get("SENSORS", "address_bmp280"), base=16), site=CONFIG.get("GENERAL", "site")),
    # SCD30(address=int(CONFIG.get("SENSORS", "address_scd30"), base=16), site=CONFIG.get("GENERAL", "site"))
]

SENSOR_ARRAY = SensorArray(SENSORS)
SECONDS_IN_MINUTE = 60


def random_time_estimator(var, target, increases=True, margin=0.1, retries=5, delay=1, unit="seconds", filename=None):
    assert 0 < margin < 1, "`margin` must lie in (0, 1)."
    current_value = SENSOR_ARRAY.read(var, delay=delay, retries=retries)
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

    if filename is not None:
        row = pd.Series([datetime.now(), var, current_value, on, t],
                        index=["taken_at", "variable", "value", "is_relay_on", "time_relay_on"])
        write_readings(row.to_frame().T, filename)

    logging.debug(f"keep device on: {on}.")
    logging.debug(f"time to keep device on: {t} {unit}.")
    return on, t * SECONDS_IN_MINUTE if unit == "minutes" else t


def _convert_time_argument(x, unit):
    return x * SECONDS_IN_MINUTE if unit == "minutes" else x


def main(args):
    root_logger = get_logger(LOG_LEVELS[args.log_level],
                             get_abs_path("logs", args.log_file) if args.log_file is not None else None)
    root_logger.info(f"start controlling {args.var}")
    root_logger.info(f"try to keep at {args.target} +/- {args.margin * 100:.2f}%.")
    root_logger.info(f"estimation strategy for turning on the device is random: " 
                     f"device may turn on for {args.active_min} to {args.active_max} {args.unit}")

    relays = [Relay(pin, active_low=False) for pin in args.relays]
    controller = Controller(relays,
                            active_min=_convert_time_argument(args.active_min, args.unit),
                            active_max=_convert_time_argument(args.active_max, args.unit),
                            delay=_convert_time_argument(args.delay, args.unit))
    controller.run(estimation_strategy=random_time_estimator,
                   var=args.var,
                   target=args.target,
                   increases=args.increases,
                   margin=args.margin,
                   unit=args.unit,
                   retries=args.sensor_retries,
                   delay=args.sensor_delay,
                   filename=get_abs_path("data", args.track_csv))


if __name__ == "__main__":
    import argparse
    import signal
    from utilities import get_logger, interrupt_handler

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("var", help="variable to control for.")
    PARSER.add_argument("target", type=float, help="target value to try and maintain.")
    PARSER.add_argument("relays", nargs="*", type=int, help="GPIO pin of relay.")
    PARSER.add_argument("--increases", action="store_true", default=False,
                        help="connected devices may in or decrease the value of the environment variable. "
                             "set flag to indicate increase in environmental variable, otherwise decreasing "
                             "behavior is assumed.")
    PARSER.add_argument("--margin", type=float, default=0.1,
                        help="margin of error in percent, i.e. default margin of 0.1 corresponds to a "
                             "10 percent interval around the target value.")
    PARSER.add_argument("--unit", choices=["seconds", "minutes"], default="minutes",
                        help="unit for time, defaults to minutes.")
    PARSER.add_argument("--sensor-retries", type=int, default=5,
                        help="how often to try and re-read the sensor in case of runtime error.")
    PARSER.add_argument("--sensor-delay", type=int, default=1,
                        help="how long to wait before trying to re-read sensor in case of runtime error.")
    PARSER.add_argument("--delay", type=int, default=1,
                        help="how long to wait in case there is no adjustment necessary - always in seconds.")
    PARSER.add_argument("--active-min", type=int, default=1,
                        help="minimum time to keep device running when turning on - depends on `unit`.")
    PARSER.add_argument("--active-max", type=int, default=10,
                        help="maximum time to keep device running when turning on - depends on `unit`.")
    PARSER.add_argument("--log-file", default=None,
                        help="file to store logs, no logs are stored if this parameter is not provided,"
                             " logs are written to `logs` directory.")
    PARSER.add_argument("--log-level", default="info", choices=["info", "warn", "debug", "error"])
    PARSER.add_argument("--track-csv", default=None,
                        help="file to track circuit actions, if this parameter is not set, keep no track record.")
    ARGS = PARSER.parse_args()

    signal.signal(signal.SIGINT, interrupt_handler)
    main(ARGS)





