import os
import sys
import time
import signal
from configparser import ConfigParser
from pathlib import Path


def get_abs_path(*args):
    return os.path.join(Path(__name__).parent.parent, *args)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def interrupt_handler(signum, frame, cleanup_func=None):
    print(f'Handling signal {signum} ({signal.Signals(signum).name}).')

    if cleanup_func:
        cleanup_func()

    time.sleep(1)
    sys.exit(0)


CONFIG = ConfigParser()
CONFIG.read(get_abs_path("config.ini"))