import os
import sys
import time
import signal
import threading
import logging
from configparser import ConfigParser, NoSectionError, NoOptionError
from pathlib import Path


EXIT_EVENT = threading.Event()
_UNSET = object()


class MyConfigParser(ConfigParser):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.read(self.path)

    def get(self, section, option, *, raw=False, vars=None, fallback=_UNSET):
        self.read(self.path)
        try:
            d = self._unify_values(section, vars)
        except NoSectionError:
            if fallback is _UNSET:
                raise
            else:
                return fallback
        option = self.optionxform(option)
        try:
            value = d[option]
        except KeyError:
            if fallback is _UNSET:
                raise NoOptionError(option, section)
            else:
                return fallback

        if raw or value is None:
            return value
        else:
            return self._interpolation.before_get(self, section, option, value,
                                                  d)

    def get_controller_config(self, var):
        self.read(self.path)
        assert var in self.sections(), f"controller config for {var} not defined in `config.ini`"
        assert var not in ["GENERAL", "SENSORS", "DATABASE"], f"{var} is not a config for a controller."
        out = {
            "var": self.get(var, "var"),
            "relays": [int(i) for i in self.get(var, "relays").split(",")],
            "active_low": self.getboolean(var, "active_low"),
            "increases": self.getboolean(var, "increases", fallback=None),
            "target": self.getfloat(var, "target", fallback=None),
            "margin": self.getfloat(var, "margin", fallback=None),
            "delay": self.getint(var, "delay"),
            "active_min": self.getint(var, "active_min"),
            "active_max": self.getint(var, "active_max"),
            "unit": self.get(var, "unit"),
            "file_name": self.get(var, "file_name", fallback=None)}
        return out


def get_abs_path(*args):
    return os.path.join(Path(__file__).parent.parent, *args)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def interrupt_handler(signum, frame):
    print(f'Handling signal {signum} ({signal.Signals(signum).name}).')

    EXIT_EVENT.set()

    time.sleep(1)
    sys.exit(0)


def get_logger(level, path_to_log_file=None, fmt=None):
    fmt = fmt if fmt is not None else "%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
    log_formatter = logging.Formatter(fmt)
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

CONFIG = MyConfigParser(path=get_abs_path("config.ini"))
