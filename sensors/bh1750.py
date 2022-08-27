import adafruit_bh1750
from sensors import Sensor, I2C


class BH1750(Sensor):

    def __init__(self, address, site):
        super(BH1750, self).__init__(site=site)
        self.measures = {"light intensity": "Lux"}
        self.device = adafruit_bh1750.BH1750(I2C, address=address)


if __name__ == "__main__":
    from utilities import CONFIG

    bh1750 = BH1750(address=CONFIG["SENSORS"]["address_bbh1750"], site=CONFIG["GENERAL"]["site"])
    readings = bh1750.read(retries=5)
    print(*readings, sep="\n")
