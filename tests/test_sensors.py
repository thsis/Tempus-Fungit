import unittest
from components import PINS, DHT22, SCD30, BH1750, BMP280, SensorArray
from utilities import CONFIG


class TestSensors(unittest.TestCase):
    def test_dht22(self):
        dht22 = DHT22(address=PINS[CONFIG.get("SENSORS", "address_dht22")],
                      site=CONFIG.get("GENERAL", "site"))
        readings = dht22.read_all()
        self.assertEqual(len(readings), len(dht22.var2unit))

    def test_bh1750(self):
        bh1750 = BH1750(address=int(CONFIG.get("SENSORS", "address_bh1750"), base=16),
                        site=CONFIG.get("GENERAL", "site"))
        readings = bh1750.read_all()
        self.assertEqual(len(readings), len(bh1750.var2unit))

    def test_bmp280(self):
        bmp280 = BMP280(address=int(CONFIG.get("SENSORS", "address_bmp280"), base=16),
                        site=CONFIG.get("GENERAL", "site"))
        readings = bmp280.read(retries=5)
        self.assertEqual(len(readings), len(bmp280.var2unit))

    def test_scd(self):
        scd30 = SCD30(address=int(CONFIG.get("SENSORS", "address_scd30"), base=16),
                      site=CONFIG.get("GENERAL", "site"))
        readings = scd30.read_all(retries=5)
        self.assertEqual(len(readings), len(scd30.var2unit))

    def test_sensor_array(self):
        sensors = [DHT22(address=PINS[CONFIG.get("SENSORS", "address_dht22")],
                         site=CONFIG.get("GENERAL", "site")),
                   BH1750(address=int(CONFIG.get("SENSORS", "address_bh1750"), base=16),
                          site=CONFIG.get("GENERAL", "site"))
                   ]
        sensor_array = SensorArray(sensors)
        sensor_readings = sensor_array.take_sensor_readings()
        self.assertEqual(len(sensor_readings), sum(len(s.var2unit) for s in sensors))




if __name__ == '__main__':
    unittest.main()
