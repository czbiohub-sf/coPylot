import logging

# Setup console handler
def get_console_handler():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_format = logging.Formatter('%(levelname)s - %(module)s.%(funcName)s - %(message)s')
    console_handler.setFormatter(console_format)
    return console_handler

# Setup file handler
def get_file_handler(filename):
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')
    file_handler.setFormatter(file_format)
    return file_handler

# Setup root logger
def configure_logger(name, filename=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler(filename)) if filename is not None else None
    logger.propagate = False
    return logger


