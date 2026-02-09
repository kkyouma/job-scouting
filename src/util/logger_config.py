"""
Centralized logger with colors to use in all scripts.
Usage: from logger_config import get_logger
"""

import logging
import sys


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Colores básicos
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Colores brillantes
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"


class ColoredFormatter(logging.Formatter):
    """Formatter que agrega colores según el nivel de log."""

    LEVEL_COLORS = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BRIGHT_RED + Colors.BOLD,
    }

    def format(self, record):
        # Guardar el levelname original
        levelname_original = record.levelname

        # Agregar color al nivel
        color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)
        record.levelname = f"{color}{record.levelname}{Colors.RESET}"

        # Formatear el mensaje
        formatted = super().format(record)

        # Restaurar el levelname original
        record.levelname = levelname_original

        return formatted


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Obtiene un logger configurado con colores.

    Args:
        name: Nombre del logger (típicamente __name__)
        level: Nivel de logging (default: INFO)

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)

    # Evitar duplicar handlers si ya existe
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Formato: [2024-02-09 10:30:45] [INFO] [script_name] Mensaje
    formatter = ColoredFormatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def get_file_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Obtiene un logger que escribe tanto a consola (con colores) como a archivo (sin colores).

    Args:
        name: Nombre del logger
        log_file: Ruta al archivo de log
        level: Nivel de logging

    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)

    # Handler para consola con colores
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    colored_formatter = ColoredFormatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(colored_formatter)

    # Handler para archivo sin colores
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    plain_formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(plain_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
