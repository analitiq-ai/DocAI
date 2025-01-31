import logging
import sys


def setup_logger(log_file="error.log", console_level=logging.INFO, file_level=logging.ERROR):
    """
    Configures the logging for the application with both console and file handlers.

    Args:
        log_file (str): The filename for the error log file.
        console_level (int): Logging level for console output (default: INFO).
        file_level (int): Logging level for file output (default: ERROR).
    """
    # Set up root logger
    logger = logging.getLogger()
    if logger.hasHandlers():  # Check if handlers already exist
        logger.handlers.clear()  # Remove all existing handlers
    logger.setLevel(logging.DEBUG)  # Set root logger level to the most verbose (allows filtering in handlers)

    # Console handler (logs to stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler (logs to a file, for errors and above)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
