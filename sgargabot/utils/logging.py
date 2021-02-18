import logging
import os

from logging.handlers import TimedRotatingFileHandler

import sgargabot.utils.config as config
from sgargabot.models.enums import LogLevel


def initialize_logging(log_level: LogLevel, log_file: str, log_folder: str):
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)-8s] - %(message)s (%(filename)s:%(lineno)s",
        "%Y-%m-%d %H:%M:%S",
    )
    root_logger = logging.getLogger()
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level.value)
    stream_handler.setFormatter(formatter)
    log_folder_abs = os.path.join(config.BASE_DIR, log_folder)
    if not os.path.isdir(log_folder_abs):
        os.mkdir(log_folder_abs)
    log_file_abs = (
        log_file if os.path.isabs(log_file) else os.path.join(log_folder_abs, log_file)
    )
    file_handler = TimedRotatingFileHandler(log_file_abs, when="midnight")
    file_handler.setLevel(log_level.value)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(log_level.value)
