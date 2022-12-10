import adafruit_bh1750
from RPi import GPIO
from components import Sensor, I2C


class BH1750(Sensor):

    def __init__(self, address, site):
        super(BH1750, self).__init__(site=site)
        self.var2unit = {"light_intensity": "Lux"}
        self.address = address
        self.device = adafruit_bh1750.BH1750(I2C, address=self.address)
        # for readability reasons: copy default name for variable
        self.device.light_intensity = self.device.lux


if __name__ == "__main__":
    from utilities import CONFIG

    bh1750 = BH1750(address=int(CONFIG.get("SENSORS", "address_bh1750"), base=16), site=CONFIG.get("GENERAL", "site"))
    readings = bh1750.read_all(retries=5)
    print(*readings, sep="\n")
