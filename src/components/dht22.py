import adafruit_dht
from src.components import Sensor
from sysv_ipc import ExistentialError


class DHT22(Sensor):

    def __init__(self, address, site):
        super(DHT22, self).__init__(site=site)
        self.var2unit = {"temperature": "C", "humidity": "%"}
        self.device = adafruit_dht.DHT22(address)

    def __del__(self):
        try:
            self.device.exit()
        except ExistentialError:
            pass


if __name__ == "__main__":
    from src.utilities import CONFIG
    from src.components import PINS

    dht22 = DHT22(address=PINS[CONFIG.get("SENSORS", "address_dht22")], site=CONFIG.get("GENERAL", "site"))
    readings = dht22.read_all(retries=5)
    print(*readings, sep="\n")
