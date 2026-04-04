"""
Centralized logger wrapper.
Usage: from src.util.logger_config import get_logger
"""

import logging


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Returns a generic Python logger.
    Handlers and formatters are deferred to Prefect or the execution context
    to prevent double-printing logs.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger


def get_file_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Returns a unified file logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == log_file for h in logger.handlers):
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s"))
        logger.addHandler(handler)
    return logger
