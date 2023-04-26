from ._general import write_readings, Sensor, SensorArray, PINS, I2C
from .bh1750 import BH1750
from .bmp280 import BMP280
from .dht22 import DHT22
from .scd30 import SCD30
from .relay import Relay
from .controller import Controller


def setup_sensors(config, dht22=True, bmp280=True, bh1750=True, scd30=True):
    assert any([dht22, bmp280, bh1750, scd30]), "Need to add at least one sensor."
    site = config.get("GENERAL", "site")
    sensors = []
    if dht22:
        sensors.append(DHT22(address=PINS[config.get("SENSORS", "address_dht22")], site=site))
    if bmp280:
        sensors.append(BMP280(address=int(config.get("SENSORS", "address_bmp280"), base=16), site=site))
    if bh1750:
        sensors.append(BH1750(address=int(config.get("SENSORS", "address_bh1750"), base=16), site=site))
    # if scd30:
    #     sensors.append(SCD30(address=int(config.get("SENSORS", "address_scd30"), base=16), site=site))
    return sensors
