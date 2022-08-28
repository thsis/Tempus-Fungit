import os
import logging
import itertools
import time

import board
import pandas as pd
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Record:
    site: str
    taken_at: datetime
    sensor: str
    variable: str
    unit: str
    value: float

    def __init__(self, site, sensor, variable, unit, value):
        self.site = site
        self.taken_at = datetime.now()
        self.sensor = sensor
        self.variable = variable
        self.unit = unit
        self.value = value

    def __str__(self):
        var_part = f"{self.variable}[{self.unit}]:".ljust(21)
        val_part = f"{self.value:.2f}".rjust(6)
        taken_at_part = f"taken at {self.taken_at.strftime('%Y-%m-%d %H:%M:%S')}."

        return f"{var_part} {val_part} {taken_at_part}"


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
    def __init__(self, sensors, outpath, retries=5):
        self.sensors = sensors
        self.outpath = outpath
        self.retries = retries
        self.buffer = []

    def __reset_buffer(self):
        self.buffer = []

    def __take_readings(self):
        readings = list(itertools.chain.from_iterable([sensor.read(retries=self.retries) for sensor in self.sensors]))
        print(*readings, sep="\n")
        self.buffer += readings

    def __flush_buffer(self):
        data = pd.DataFrame(self.buffer)
        data.to_csv(self.outpath, index=False, mode="a", header=not os.path.exists(self.outpath))
        return data

    def read(self, delay=5, flush_after=5):
        while True:
            try:
                for _ in range(flush_after):
                    self.__take_readings()

                data = self.__flush_buffer()
                print(data.tail())
                self.__reset_buffer()
                time.sleep(delay)
            except Exception as e:
                logger.exception(e)
                self.__flush_buffer()
            except KeyboardInterrupt:
                self.__flush_buffer()


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
