import os
from configparser import ConfigParser
from pathlib import Path


def get_abs_path(*args):
    return os.path.join(Path(__name__).parent.parent, *args)


CONFIG = ConfigParser()
CONFIG.read(get_abs_path("config.ini"))