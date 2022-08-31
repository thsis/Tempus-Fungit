from datetime import datetime
from dataclasses import dataclass


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
        val_part = f"{self.value:.2f}".rjust(6) if self.value is not None else "N/A"
        taken_at_part = f"taken at {self.taken_at.strftime('%Y-%m-%d %H:%M:%S')}."

        return f"{var_part} {val_part} {taken_at_part}"
