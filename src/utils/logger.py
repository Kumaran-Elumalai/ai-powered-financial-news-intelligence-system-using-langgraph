import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
