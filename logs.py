import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

LOG_PATH: str = 'logs'
FORMATTER = logging.Formatter(
    '[{asctime}] {levelname:<8} {name:<9} {message}',  # TODO: hardcoded width
    style='{',
    datefmt='%d.%m.%y %H:%M:%S'
)


def get_logger(name: str) -> logging.Logger:
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)

    logger = logging.getLogger(name)

    handler = TimedRotatingFileHandler(
        filename=f'{LOG_PATH}/{name}.log',
        when='midnight'
    )
    handler.setFormatter(FORMATTER)
    handler.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
    logger.addHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(FORMATTER)
    handler.setLevel(os.getenv('LOG_LEVEL', 'INFO'))
    logger.addHandler(handler)

    logger.setLevel(os.getenv('LOG_LEVEL', 'INFO'))

    return logger
