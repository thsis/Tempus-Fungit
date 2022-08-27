import adafruit_bh1750
from sensors import Sensor, I2C


class BH1750(Sensor):
    measures = ["lux"]

    def __init__(self, address):
        super(BH1750, self).__init__()
        self.device = adafruit_bh1750.BH1750(I2C, address=address)


if __name__ == "__main__":
    bh1750 = BH1750(address=0x23)
    lux = bh1750.read(retries=5)
    print(f"Light Intensity: {lux:2.f} Lux")
