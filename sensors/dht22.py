import adafruit_dht
from sensors import Sensor


class DHT22(Sensor):
    measures = ["temperature", "humidity"]

    def __init__(self, pin):
        super(DHT22, self).__init__()
        self.device = adafruit_dht.DHT22(pin)


if __name__ == "__main__":
    import board
    # todo: read pin from config file
    dht22 = DHT22(board.D4)
    temperature, humidity = dht22.read(retries=5)
    print(f"Temperature: {temperature:.2f}*C", f"Humidity: {humidity:.2f}%", sep="\n")
