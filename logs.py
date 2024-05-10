import logging
import os
import sys
from logging import FileHandler
from classes.csv_formatter import CsvFormatter

LOG_PATH: str = 'logs'
LOG_LEVEL = os.getenv('LOG_LEVEL') or 'INFO'


def get_logger(name: str) -> logging.Logger:
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)

    logger = logging.getLogger(name)

    handler = FileHandler(f'{LOG_PATH}/log.csv')
    handler.setFormatter(
        CsvFormatter(
            attrs=('asctime', 'levelname', 'name', 'message', 'created'),
            datefmt='%d.%m.%y %H:%M:%S'
        )
    )
    handler.setLevel(LOG_LEVEL)
    logger.addHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            '[{asctime}] {levelname:<8} {name:<9} {message}',  # TODO: hardcoded width
            style='{', datefmt='%d.%m.%y %H:%M:%S'
        )
    )
    handler.setLevel(LOG_LEVEL)
    logger.addHandler(handler)

    logger.setLevel(LOG_LEVEL)

    return logger


def get_skipped_logger() -> logging.Logger:
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)

    logger = logging.getLogger('skipped')
    logger.setLevel(logging.WARNING)

    handler = FileHandler(f'{LOG_PATH}/no_sample.log')
    handler.setLevel(LOG_LEVEL)
    logger.addHandler(handler)
    return logger
