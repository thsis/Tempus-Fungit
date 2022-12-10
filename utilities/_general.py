import os
import sys
import time
import signal
import logging
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


def get_logger(level, path_to_log_file=None):
    log_formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
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
    "error": logging.ERROR
}
CONFIG = ConfigParser()
CONFIG.read(get_abs_path("config.ini"))