from numpy.random import normal, uniform, exponential
from utilities import Record


def make_sampler(sampler, **kwargs):
    def func():
        return sampler(**kwargs)
    return func


class Sensor:
    def __init__(self):
        self.temperature = make_sampler(normal, loc=25, scale=0.5)
        self.humidity = make_sampler(uniform, low=0, high=100)
        self.co2 = make_sampler(normal, loc=400, scale=100)
        self.light_intensity = make_sampler(exponential, scale=4)
        self.pressure = make_sampler(normal, loc=1000, scale=200)
        self.altitude = make_sampler(uniform, low=454, high=454)


class MockSensor:
    def __init__(self):
        self.device = Sensor()
        self.site = "Test-Suite"

    def read(self):
        dev = self.device
        site = self.site
        sensor = self.__class__.__name__
        reading = [Record(site, sensor, var, unit, getattr(dev, var).__call__()) for var, unit in self.var2unit.items()]
        return reading


class MockDHT22(MockSensor):
    var2unit = {"temperature": "C", "humidity": "%"}

    def __init__(self, site):
        super(MockDHT22, self).__init__()
        self.site = site


class MockBH1750(MockSensor):
    var2unit = {"light_intensity": "Lux"}

    def __init__(self, site):
        super(MockBH1750, self).__init__()
        self.site = site


class MockBMP280(MockSensor):
    var2unit = {"temperature": "C",
                "pressure": "hPa",
                "altitude": "m"}

    def __init__(self, site):
        super(MockBMP280, self).__init__()
        self.site = site


if __name__ == "__main__":
    from pandas import DataFrame
    from utilities import CONFIG

    SITE = CONFIG.get("GENERAL", "site")

    dht22 = MockDHT22(site=SITE)
    bh1750 = MockBH1750(site=SITE)
    bmp280 = MockBMP280(site=SITE)

    for mocked_sensor in dht22, bh1750, bmp280:
        print(*mocked_sensor.read(), sep="\n")
