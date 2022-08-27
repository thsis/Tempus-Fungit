import adafruit_dht
from sensors import Sensor


class DHT22(Sensor):

    def __init__(self, address, site):
        super(DHT22, self).__init__(site=site)
        self.measures = {"temperature": "C", "humidity": "%"}
        self.device = adafruit_dht.DHT22(address)


if __name__ == "__main__":
    from utilities import CONFIG
    from sensors import PINS

    dht22 = DHT22(address=PINS[CONFIG["SENSORS"]["address_dht22"]], site=CONFIG["GENERAL"]["site"])
    readings = dht22.read(retries=5)
    print(*readings, sep="\n")
