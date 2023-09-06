try:
    from ._version import version as __version__
except ImportError:
    __version__ = "not-installed"

import logging


def enable_logging(
    log_filepath: str = 'copylot_debug_log.txt',
    level = logging.DEBUG,
):
    """
    Enable debug logging to a text file

    Parameters
    ----------
    log_filepath : str
        Path to log file, by default 'copylot_debug_log.txt'
    """
    # create file handler which logs debug messages
    fh = logging.FileHandler(log_filepath)
    fh.setLevel(level)
    fh.setFormatter(formatter)

    logger.addHandler(fh)


logger = logging.getLogger('copylot')
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s'
)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(ch)
