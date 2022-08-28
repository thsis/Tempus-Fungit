from numpy.random import normal, uniform, exponential
from sensors import Record, DHT22, BH1750, BMP280


def make_sampler(sampler, **kwargs):
    def func():
        return sampler(**kwargs)
    return func


class MockSensorMixin:
    def __init__(self):
        self.device = {
            "temperature": make_sampler(normal, loc=25, scale=0.5),
            "humidity": make_sampler(uniform, low=0, high=100),
            "co2": make_sampler(normal, loc=400, scale=100),
            "light_intensity": make_sampler(exponential, scale=4),
            "pressure": make_sampler(normal, loc=1000, scale=200),
            "altitude": make_sampler(uniform, low=454, high=454)}

    def read(self, retries=5):
        dev = self.device
        site = self.site
        sensor = self.__class__.__name__
        reading = [Record(site, sensor, var, unit, getattr(dev, var).__call__()) for var, unit in self.var2unit.items()]
        return reading


class MockDHT22(MockSensorMixin, DHT22):
    def __init__(self, site):
        super(MockDHT22, self).__init__()
        self.site = site


class MockBH1750(MockSensorMixin, BH1750):
    def __init__(self, site):
        super(MockBH1750, self).__init__()
        self.site = site


class MockBMP280(MockSensorMixin, BMP280):
    def __init__(self, site):
        super(MockBMP280, self).__init__()
        self.site = site


if __name__ == "__main__":
    from utilities import CONFIG

    SITE = CONFIG.get("GENERAL", "site")

    dht22 = MockDHT22(site=SITE)
    bh1750 = MockBH1750(site=SITE)
    bmp280 = MockBMP280(site=SITE)

    for sensor in dht22, bh1750, bmp280:
        print(sensor.read(), sep="\n")
