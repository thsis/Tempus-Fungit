import signal
from utilities import CONFIG, get_logger, get_abs_path, LOG_LEVELS, interrupt_handler
from components import setup_sensors, SensorArray


def main():
    sensors = setup_sensors(CONFIG)
    out_path = get_abs_path("data", CONFIG.get("GENERAL", "env_data_file_name"))

    sensor_array = SensorArray(sensors,
                               out_path=out_path,
                               retries=CONFIG.getint("SENSORS", "retries"),
                               delay=CONFIG.getint("SENSORS", "delay"))

    sensor_array.read_all()


if __name__ == "__main__":
    LOG_PATH = get_abs_path("logs", "read_sensors.log")
    LOGGER = get_logger(LOG_LEVELS["debug"], LOG_PATH,
                        fmt="%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s")
    signal.signal(signal.SIGINT, interrupt_handler)
    main()
