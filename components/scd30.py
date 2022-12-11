import adafruit_scd30
from components import Sensor, I2C


class SCD30(Sensor):
    def __init__(self, address, site):
        super(SCD30, self).__init__(site=site)
        self.var2unit = {"temperature": "C",
                         "humidity": "%",
                         "co2": "ppm"}
        self.device = adafruit_scd30.SCD30(I2C, address=address)
        # for readability reasons: copy default names for variables
        self.device.humidity = self.device.relative_humidity
        self.device.co2 = self.device.CO2

        self.read_all(retries=1)


if __name__ == "__main__":
    from utilities import CONFIG

    scd30 = SCD30(address=int(CONFIG.get("SENSORS", "address_scd30"), base=16), site=CONFIG.get("GENERAL", "site"))
    readings = scd30.read_all(retries=5)
    print(*readings, sep="\n")
