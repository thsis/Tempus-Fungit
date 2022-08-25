import adafruit_bmp280
from sensors import Sensor, I2C


class BMP280(Sensor):
    measures = ["temperature", "pressure", "altitude"]
    sea_level_pressure = 1010.2

    def __init__(self, address):
        super(BMP280, self).__init__()
        self.device = adafruit_bmp280.Adafruit_BMP280_I2C(I2C, address=address)
        self.device.sea_level_pressure = self.sea_level_pressure


if __name__ == "__main__":
    # todo: read i2c-address from config file
    bmp280 = BMP280(address=0x76)
    temp, press, alt = bmp280.read(retries=5)
    print(f"Temperature: {temp} °C", f"Pressure: {press} hPa", f"Altitude: {alt} m", sep="\n")
