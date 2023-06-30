import signal
import subprocess
import pandas as pd
from collections import defaultdict
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from src.utilities import get_abs_path, CONFIG, interrupt_handler
plt.style.use("dark_background")

LINESTYLES = defaultdict(lambda: "-")
LINESTYLES.update(Averaged="--")

COLORS = {"Averaged": "grey",
          "SCD30": "red",
          "BMP280": "blue",
          "BH1750": "green",
          "DHT22": "orange"}


data_path = get_abs_path("data", CONFIG["GENERAL"]["env_data_file_name"])
fig, axes = plt.subplots(2, 2, sharex=True, sharey=False)


def get_data():
    data = pd.read_csv(data_path, parse_dates=["taken_at"])
    averaged = (data
                .assign(taken_at=lambda x: x.taken_at.round("min"))
                .groupby(["taken_at", "site", "variable", "unit"])
                .value
                .mean()
                .reset_index()
                .assign(sensor="Averaged"))
    df = pd.concat([data, averaged.loc[averaged.taken_at <= data.taken_at.max()]], axis=0)
    out = (df
           .loc[df.taken_at > df.taken_at.max() - pd.Timedelta(days=2)]
           .sort_values(["variable", "sensor", "taken_at"])
           .reset_index(drop=True))
    return out


def pretty_label(label):
    if label in ["co2"]:
        return label.upper()
    else:
        return " ".join([lab.capitalize() for lab in label.split("_")])


def plot(fig_path=None):
    df = get_data()
    variables = ["temperature", "humidity", "light_intensity", "co2"]
    for var, ax in zip(variables, axes.flatten()):
        ax.clear()
        ax.set_title(pretty_label(var))

        for spine in "top", "right":
            ax.spines[spine].set_visible(False)

        tmp = df.loc[df.variable == var]
        for sensor in tmp.sensor.unique():
            tmp = df.loc[(df.variable == var) & (df.sensor == sensor)]
            ax.plot(tmp.taken_at, tmp.value, label=sensor,
                    ls=LINESTYLES[sensor],
                    color=COLORS[sensor])

        ax.set_ylabel(tmp.unit.iloc[0])
        ax.legend(frameon=False, loc="lower left")

    for col in 0, 1:
        axes[-1, col].set_xlabel("Time")
        for i, label in enumerate(axes[-1, col].xaxis.get_ticklabels()):
            label.set_visible(i % 3 == 0)

    if fig_path:
        fig.savefig(fig_path)


def animate(i):
    plot()


def monitor():
    cmd = "python " + get_abs_path("src", "monitoring", "_monitor.py")
    subprocess.call(cmd, shell=True)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interrupt_handler)
    animation = FuncAnimation(plt.gcf(), animate)
    plt.tight_layout()
    plt.show()
