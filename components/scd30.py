import adafruit_scd30
import busio
import board
from components import Sensor

I2C = busio.I2C(board.SCL, board.SDA, frequency=50_000)


class SCD30(Sensor):
    def __init__(self, address, site):
        super(SCD30, self).__init__(site=site)
        self.var2unit = {"temperature": "C",
                         "relative_humidity": "%",
                         "CO2": "ppm"}
        self.device = adafruit_scd30.SCD30(I2C, address=address)


if __name__ == "__main__":
    from utilities import CONFIG

    scd30 = SCD30(address=int(CONFIG.get("SENSORS", "address_scd30"), base=16), site=CONFIG.get("GENERAL", "site"))
    readings = scd30.read_all(retries=5)
    print(*readings, sep="\n")
