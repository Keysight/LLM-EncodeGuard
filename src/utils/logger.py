"""
Logging Utilities

Provides logging and banner display functionality.
"""

import pyfiglet
import logging
from typing import Optional


def display_banner(title: str = "LLM System Prompt Leakage"):
    """
    Display ASCII art banner.

    Args:
        title: Title text to display
    """
    try:
        ascii_banner = pyfiglet.figlet_format(title)
        print(ascii_banner)
    except Exception:
        # Fallback if pyfiglet is not available
        print(f"\n{'='*60}")
        print(f"{title:^60}")
        print(f"{'='*60}\n")


def setup_logger(name: str, level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup a logger with console and optional file output.

    Args:
        name: Name of the logger
        level: Logging level (default: INFO)
        log_file: Optional path to log file

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
