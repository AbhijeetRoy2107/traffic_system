import logging
import os


def setup_logger(

    name="traffic_system",

    log_file="logs/system.log",

    level=logging.INFO
):

    os.makedirs(
        "logs",
        exist_ok=True
    )

    logger = logging.getLogger(
        name
    )

    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # =====================================================
    # FORMATTER
    # =====================================================
    formatter = logging.Formatter(

        "[%(asctime)s] "

        "[%(levelname)s] "

        "%(message)s"
    )

    # =====================================================
    # CONSOLE
    # =====================================================
    console_handler = (
        logging.StreamHandler()
    )

    console_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        console_handler
    )

    # =====================================================
    # FILE
    # =====================================================
    file_handler = logging.FileHandler(
        log_file
    )

    file_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    return logger