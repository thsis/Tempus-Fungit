import os
import sys
import time
import signal
import logging
from configparser import ConfigParser
from pathlib import Path


class MyConfigParser(ConfigParser):
    def __int__(self, *args, **kwargs):
        super().__int__(*args, **kwargs)

    def get_controller_config(self, var):
        assert var in self.sections(), f"controller config for {var} not defined in `config.ini`"
        assert var not in ["GENERAL", "SENSORS", "DATABASE"], f"{var} is not a config for a controller."
        out = {
            "var": self.get(var, "var"),
            "relays": [int(i) for i in self.get(var, "relays").split(",")],
            "active_low": self.getboolean(var, "active_low"),
            "increases": self.getboolean(var, "increases"),
            "target": self.getfloat(var, "target"),
            "margin": self.getfloat(var, "margin"),
            "delay": self.getint(var, "delay"),
            "active_min": self.getint(var, "active_min"),
            "active_max": self.getint(var, "active_max"),
            "unit": self.get(var, "unit"),
            "file_name": self.get(var, "file_name")}
        return out


def get_abs_path(*args):
    return os.path.join(Path(__file__).parent.parent, *args)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def interrupt_handler(signum, frame, cleanup_func=None):
    print(f'Handling signal {signum} ({signal.Signals(signum).name}).')

    if cleanup_func:
        cleanup_func()

    time.sleep(1)
    sys.exit(0)


def get_logger(level, path_to_log_file=None):
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s] %(message)s")
    logger = logging.getLogger()
    logger.setLevel(level)

    if path_to_log_file:
        file_handler = logging.FileHandler(path_to_log_file)
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)
    return logger


LOG_LEVELS = {
    "info": logging.INFO,
    "warn": logging.WARNING,
    "debug": logging.DEBUG,
    "error": logging.ERROR}

CONFIG = MyConfigParser()
CONFIG.read(get_abs_path("config.ini"))
