import argparse
from utilities import get_abs_path, CONFIG
from sensors import DHT22, BH1750, BMP280, SensorArray, PINS

# parser = argparse.ArgumentParser(description="Read Sensor Output")
# parser.add_argument("--ret")

DATA_PATH = get_abs_path("data", "sensor_output_raw.csv")
SENSORS = [
    DHT22(address=PINS[CONFIG.get("SENSORS", "address_dht22")], site=CONFIG.get("GENERAL", "site")),
    BH1750(address=int(CONFIG.get("SENSORS", "address_bh1750"), base=16), site=CONFIG.get("GENERAL", "site")),
    BMP280(address=int(CONFIG.get("SENSORS", "address_bmp280"), base=16), site=CONFIG.get("GENERAL", "site"))
]

sensor_array = SensorArray(SENSORS, outpath=DATA_PATH, retries=5)
sensor_array.read()