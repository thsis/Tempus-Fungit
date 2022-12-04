import argparse
import logging
import signal
from utilities import get_abs_path, CONFIG, interrupt_handler
from components import DHT22, BH1750, BMP280, SCD30, SensorArray, PINS

DATA_PATH = get_abs_path("data", "sensor_output_raw.csv")
SENSORS = [
    DHT22(address=PINS[CONFIG.get("SENSORS", "address_dht22")], site=CONFIG.get("GENERAL", "site")),
    BH1750(address=int(CONFIG.get("SENSORS", "address_bh1750"), base=16), site=CONFIG.get("GENERAL", "site")),
    BMP280(address=int(CONFIG.get("SENSORS", "address_bmp280"), base=16), site=CONFIG.get("GENERAL", "site")),
    SCD30(address=int(CONFIG.get("SENSORS", "address_scd30"), base=16), site=CONFIG.get("GENERAL", "site"))
]


def main(delay, retries):
    sensor_array = SensorArray(SENSORS, out_path=DATA_PATH, retries=5)
    sensor_array.read_all(delay=delay, retries=retries)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read Sensor Output")
    parser.add_argument("--every", type=int, default=15)
    parser.add_argument("--retries", type=int, default=15)
    args = parser.parse_args()
    logging.basicConfig(format="[%(levelname)s] %(asctime)s %(message)s", level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    signal.signal(signal.SIGINT, interrupt_handler)
    main(args.every, args.retries)
