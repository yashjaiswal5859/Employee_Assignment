import logging
from logging.handlers import RotatingFileHandler
import os
import sys


class ColoredFormatter(logging.Formatter):
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"

    def format(self, record):
        # Red for ERROR and above, Yellow for WARNING, Green for INFO/DEBUG
        if record.levelno >= logging.ERROR:
            color = self.RED
        elif record.levelno == logging.WARNING:
            color = self.YELLOW
        else:
            color = self.GREEN

        orig_levelname = record.levelname
        record.levelname = f"{color}{record.levelname}{self.RESET}"

        result = super().format(record)
        record.levelname = orig_levelname
        return result


def setup_logging(debug=True):
    log_level = logging.DEBUG if debug else logging.INFO

    log_format = "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d]: %(message)s"

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to prevent duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Console Handler (writes to sys.stdout with ColoredFormatter)
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = ColoredFormatter(log_format)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # Rotating File Handler (writes plain text to logs/app.log)
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, "app.log")

    file_formatter = logging.Formatter(log_format)
    file_handler = RotatingFileHandler(
        file_path,
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)
    root_logger.addHandler(file_handler)

    # Mute third-party library verbose logs under non-debug runs
    if not debug:
        logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
        logging.getLogger("werkzeug").setLevel(logging.WARNING)
    else:
        logging.getLogger("sqlalchemy").setLevel(logging.INFO)
        logging.getLogger("werkzeug").setLevel(logging.INFO)

    logging.info("Structured logging framework initialized.")
