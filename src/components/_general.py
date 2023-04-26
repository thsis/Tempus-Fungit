import os
import logging
import itertools
import time
import board
import pandas as pd
from src.utilities import Record, EXIT_EVENT


logger = logging.getLogger(__name__)
SENSOR_WEIGHTS = pd.DataFrame({
    "sensor": [*["SCD30"] * 3, *["DHT22"] * 2, "BH1750", *["BMP280"] * 3],
    "variable": ["temperature", "humidity", "co2",
                 "temperature", "humidity",
                 "light_intensity",
                 "temperature", "pressure", "altitude"],
    "weight": [1, 1, 1, 1, 1, 1, 1, 1, 1]
})


def write_readings(readings, out_path):
    if not os.path.exists(out_path):
        readings.to_csv(out_path, index=False)
    else:
        readings.to_csv(out_path, header=None, mode="a", index=False)


class Sensor:
    def __init__(self, site):
        self.site = site
        self.var2unit = dict()
        self.device = dict()
        super(Sensor, self).__init__()

    def read_all(self, retries=5, delay=1):
        readings = [self.read(var=var, retries=retries, delay=delay) for var in self.var2unit.keys()]
        return readings

    def read(self, var, retries=5, delay=1):
        sensor_name = self.__class__.__name__
        assert var in self.var2unit.keys(), f"{sensor_name} is not a sensor for '{var}'. Maybe check spelling?"
        unit = self.var2unit[var]
        for i in range(retries):
            try:
                reading = Record(self.site,
                                 sensor_name,
                                 var,
                                 unit,
                                 getattr(self.device, var))
                assert reading.value is not None, f"could not read {var} on sensor {sensor_name}."
                return reading
            except (RuntimeError, AssertionError) as e:
                logger.warning(e)
                time.sleep(delay)
                if i + 1 == retries:
                    logger.error(e)
                continue
        else:
            return Record(self.site, sensor_name, var, unit, None)


class SensorArray:
    def __init__(self, sensors, out_path=None, retries=5, delay=1):
        self.sensors = sensors
        self.out_path = out_path
        self.retries = retries
        self.delay = delay

    def take_sensor_readings(self):
        readings = list(
            itertools.chain.from_iterable(
                [sensor.read_all(retries=self.retries) for sensor in self.sensors]))
        for r in readings:
            if r.value:
                logger.debug(f"{r.sensor} {r.variable}: {r.value:.2f} {r.unit}")
            else:
                logger.debug(f"could not read {r.variable} on sensor {r.sensor}")
        out = pd.DataFrame(readings)
        return out

    def read(self, var, retries=None, delay=None):
        retries = retries if retries is not None else self.retries
        delay = delay if delay is not None else self.delay
        readings = pd.DataFrame(s.read(var, retries, delay) for s in self.sensors if var in s.var2unit.keys())
        if readings:
            print(readings)
            print(SENSOR_WEIGHTS)
            merged = readings.merge(SENSOR_WEIGHTS)
            # todo: implement weighted mean
            return merged.loc[merged.weight > 0].value.mean()
        else:
            return readings

    def read_all(self, delay=None, retries=None):
        retries = retries if retries is not None else self.retries
        delay = delay if delay is not None else self.delay
        while True:
            if EXIT_EVENT.is_set():
                break
            for i in range(retries):
                try:
                    results = self.take_sensor_readings()
                    if self.out_path:
                        write_readings(results, self.out_path)
                    logger.debug(f"sleeping for {delay} seconds.")
                    time.sleep(delay)
                    break

                except Exception as e:
                    if i + 1 == retries:
                        logger.exception(e)

                except KeyboardInterrupt:
                    break


I2C = board.I2C()
PINS = {"0": board.D0, 0: board.D0,
        "1": board.D1, 1: board.D1,
        "2": board.D2, 2: board.D2,
        "3": board.D3, 3: board.D3,
        "4": board.D4, 4: board.D4,
        "5": board.D5, 5: board.D5,
        "6": board.D6, 6: board.D6,
        "7": board.D7, 7: board.D7,
        "8": board.D8, 8: board.D8,
        "9": board.D9, 9: board.D9,
        "10": board.D10, 10: board.D10,
        "11": board.D11, 11: board.D11,
        "12": board.D12, 12: board.D12,
        "13": board.D13, 13: board.D13,
        "14": board.D14, 14: board.D14,
        "15": board.D15, 15: board.D15,
        "16": board.D16, 16: board.D16,
        "17": board.D17, 17: board.D17,
        "18": board.D18, 18: board.D18,
        "19": board.D19, 19: board.D19,
        "20": board.D20, 20: board.D20,
        "21": board.D21, 21: board.D21,
        "22": board.D22, 22: board.D22,
        "23": board.D23, 23: board.D23,
        "24": board.D24, 24: board.D24,
        "25": board.D25, 25: board.D25,
        "26": board.D26, 26: board.D26,
        "27": board.D27, 27: board.D27}
