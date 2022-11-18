import adafruit_bmp280
from components import Sensor, I2C


class BMP280(Sensor):

    def __init__(self, address, site):
        super(BMP280, self).__init__(site=site)
        self.var2unit = {"temperature": "C",
                         "pressure": "hPa",
                         "altitude": "m"}
        self.sea_level_pressure = 1010.2
        self.device = adafruit_bmp280.Adafruit_BMP280_I2C(I2C, address=address)
        self.device.sea_level_pressure = self.sea_level_pressure


if __name__ == "__main__":
    from utilities import CONFIG

    bmp280 = BMP280(address=int(CONFIG.get("SENSORS", "address_bmp280"), base=16), site=CONFIG.get("GENERAL", "site"))
    readings = bmp280.read(retries=5)
    print(*readings, sep="\n")
