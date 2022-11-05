import os
import sys
import logging
import itertools
import time
import board
import pandas as pd

from utilities import Record, clear

logger = logging.getLogger(__name__)


class Sensor:
    def __init__(self, site):
        self.site = site
        self.var2unit = dict()
        self.device = dict()
        super(Sensor, self).__init__()

    def read(self, retries=5):
        dev = self.device
        site = self.site
        sensor = self.__class__.__name__
        for _ in range(retries):
            try:
                reading = [Record(site, sensor, var, unit, getattr(dev, var)) for var, unit in self.var2unit.items()]
                return reading
            except RuntimeError:
                continue
        else:
            return (None for _ in self.var2unit)


class SensorArray:
    def __init__(self, sensors, out_path, retries=5):
        self.sensors = sensors
        self.out_path = out_path
        self.retries = retries
        self.buffer = []

    def take_sensor_readings(self):
        readings = list(itertools.chain.from_iterable([sensor.read(retries=self.retries) for sensor in self.sensors]))
        print(*readings, sep="\n")
        print()
        return pd.DataFrame(readings)

    def write_sensor_readings(self, readings):
        if not os.path.exists(self.out_path):
            readings.write(self.out_path, index=False)
        else:
            readings.write(self.out_path, header=None, mode="a", index=False)

    def read(self, delay=5, retries=5):
        while True:
            for i in range(retries):
                try:
                    results = self.take_sensor_readings()
                    self.write_sensor_readings(results)
                    time.sleep(delay)
                    # clear screen
                    clear()
                    break

                except Exception as e:
                    if i + 1 == retries:
                        logger.exception(e)

                except KeyboardInterrupt:
                    break


I2C = board.I2C()
PINS = {"0": board.D0,
        "1": board.D1,
        "2": board.D2,
        "3": board.D3,
        "4": board.D4,
        "5": board.D5,
        "6": board.D6,
        "7": board.D7,
        "8": board.D8,
        "9": board.D9,
        "10": board.D10,
        "11": board.D11,
        "12": board.D12,
        "13": board.D13,
        "14": board.D14,
        "15": board.D15,
        "16": board.D16,
        "17": board.D17,
        "18": board.D18,
        "19": board.D19,
        "20": board.D20,
        "21": board.D21,
        "22": board.D22,
        "23": board.D23,
        "24": board.D24,
        "25": board.D25,
        "26": board.D26,
        "27": board.D27}
