import signal
import threading
import time
from datetime import datetime, timedelta
from src.utilities import get_abs_path, CONFIG, interrupt_handler, get_logger, LOG_LEVELS, monitor, plot
from src.components import Controller, setup_sensors, SensorArray


def main(wait, write_every=1, display=True, notify=True):
    if display:
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        monitor_thread.join()

    iteration = 0
    day_1 = datetime.now() - timedelta(days=1)

    while True:
        iteration += 1
        day_1, day_2 = datetime.now(), day_1

        # control environment
        CONFIG.update()
        env_state = SENSOR_ARRAY.get_state()
        CONTROLLER.control(env_state)

        # write to csv
        if iteration % write_every:
            SENSOR_ARRAY.read_all()

        # send photo and monitor plot
        if notify and day_1.date() != day_2.date():
            # todo: add functionality for sending emails
            plot(FIG_PATH)

        time.sleep(wait)


if __name__ == "__main__":
    import argparse
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("wait", type=int, help="seconds to wait between relay adjustments")
    PARSER.add_argument("--write-every", type=int, default=1, help="report the sensor readings every x iterations")
    PARSER.add_argument("--no-display", action="store_true", default=False)
    PARSER.add_argument("--no-notify", action="store_true", default=False)
    PARSER.add_argument("--log-level", choices=["debug", "info", "warn", "error"], default="error")
    ARGS = PARSER.parse_args()

    SECTIONS = ["CONTROLLER_CO2", "CONTROLLER_HUMIDITY", "CONTROLLER_LIGHTS"]
    LOG_PATH = get_abs_path("logs", "main.log")
    FIG_PATH = get_abs_path("figures", CONFIG.get("GENERAL", "monitor_file_name"))
    LOGGER = get_logger(LOG_LEVELS["debug"], LOG_PATH,
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
