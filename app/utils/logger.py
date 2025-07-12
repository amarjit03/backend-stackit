# logger.py

import logging
import os

def get_logger(name: str) -> logging.Logger:
    """Creates or retrieves a logger instance with the given name."""
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Prevent adding multiple handlers if already set
        logger.setLevel(logging.DEBUG)

        # Create logs directory if not exists
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/app.log")
        console_handler = logging.StreamHandler()

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

