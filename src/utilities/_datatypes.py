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
        self.var_synonyms = {
            "relative_humidity": "humidity",
            "CO2": "co2"
        }
        self.site = site
        self.taken_at = datetime.now()
        self.sensor = sensor
        # different sensors can have different names for the same variable
        self.variable = self.var_synonyms.get(variable, variable)
        self.unit = unit
        self.value = value

    def __str__(self):
        var_part = f"{self.variable}[{self.unit}]:".ljust(21)
        val_part = f"{self.value:.2f}".rjust(10) if self.value is not None else "N/A".rjust(10)
        taken_at_part = f"taken at {self.taken_at.strftime('%Y-%m-%d %H:%M:%S')}"
        by_part = f"by sensor {self.sensor}"

        return f"{var_part} {val_part} {taken_at_part} {by_part}"
