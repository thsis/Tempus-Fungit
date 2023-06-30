import signal
import threading
import time
from src.utilities import get_abs_path, CONFIG, interrupt_handler, get_logger, LOG_LEVELS
from src.monitoring import monitor, plot, take_photo, send_email
from src.components import Controller, setup_sensors, SensorArray

SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE
SECONDS_PER_DAY = 24 * SECONDS_PER_HOUR


def iteration_to_time_period_converter(wait_period, activate_every="day"):
    i = -1
    seconds = {"minute": SECONDS_PER_MINUTE, "hour": SECONDS_PER_HOUR, "day": SECONDS_PER_DAY}
    mod = seconds[activate_every] // wait_period
    while True:
        i += 1
        yield i % mod == 0


def main(wait, write_every="hour", photo_every="day", display=True, notify=True):
    write = iteration_to_time_period_converter(wait, write_every)
    photo = iteration_to_time_period_converter(wait, photo_every)

    if display:
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    iteration = -1

    while True:
        iteration += 1

        # control environment
        CONFIG.update()
        env_state = SENSOR_ARRAY.get_state()
        CONTROLLER.control(env_state)

        # write to csv
        if next(write):
            SENSOR_ARRAY.read_all()

        # send photo and monitor plot
        if next(photo):
            plot(FIG_PATH)
            take_photo(PHOTO_PATH)
            send_email()

        time.sleep(wait)


if __name__ == "__main__":
    import argparse
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("wait", type=int, help="seconds to wait between relay adjustments")
    PARSER.add_argument("--write-every", type=int, default=1, help="report the sensor readings every x iterations")
    PARSER.add_argument("--no-display", action="store_true", default=False)
    PARSER.add_argument("--no-notify", action="store_true", default=False)
    PARSER.add_argument("--log-level", choices=["debug", "info", "warn", "error"], default="error",
                        help="controls detail of logs")
    ARGS = PARSER.parse_args()

    SECTIONS = ["CONTROLLER_CO2", "CONTROLLER_HUMIDITY", "CONTROLLER_LIGHTS"]
    LOG_PATH = get_abs_path("logs", "main.log")
    FIG_PATH = get_abs_path("figures", CONFIG.get("GENERAL", "monitor_file_name"))
    PHOTO_PATH = get_abs_path("figures", CONFIG.get("GENERAL", "photo_file_name"))
    LOGGER = get_logger(LOG_LEVELS[ARGS.log_level], LOG_PATH,
                        fmt="%(asctime)s [%(levelname)s] [%(threadName)s] [%(funcName)s] %(message)s")

    SENSORS = setup_sensors(CONFIG)

    SENSOR_ARRAY = SensorArray(SENSORS,
                               out_path=get_abs_path("data", CONFIG.get("GENERAL", "env_data_file_name")),
                               retries=CONFIG.getint("SENSORS", "retries"),
                               delay=CONFIG.getint("SENSORS", "delay"))
    CONTROLLER = Controller(sections=SECTIONS)

    signal.signal(signal.SIGINT, interrupt_handler)
    main(wait=ARGS.wait,
         write_every=ARGS.write_every,
         display=not ARGS.no_display,
         notify=not ARGS.no_notify)
