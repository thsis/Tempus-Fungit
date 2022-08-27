import board


class Sensor:
    def __init__(self):
        self.measures = []
        self.device = {}
        super(Sensor, self).__init__()

    def read(self, retries=5):
        for _ in range(retries):
            try:
                return (getattr(self.device, measure) for measure in self.measures)
            except RuntimeError:
                continue
        else:
            return (None for _ in self.measures)


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
