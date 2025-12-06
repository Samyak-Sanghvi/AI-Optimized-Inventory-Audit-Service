# logger.py
import logging
from logging.handlers import RotatingFileHandler
import sys

# -----------------------------
# Logger Configuration
# -----------------------------
LOG_FILE = "app.log"           # log file name
MAX_BYTES = 5 * 1024 * 1024    # 5 MB per file
BACKUP_COUNT = 5               # keep 5 old log files

logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)  # default logging level

# -----------------------------
# Console Handler
# -----------------------------
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # info and above to console

console_format = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(console_format)
logger.addHandler(console_handler)

# -----------------------------
# File Handler (Rotating)
# -----------------------------
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT)
file_handler.setLevel(logging.DEBUG)  # log everything to file

file_format = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(file_format)
logger.addHandler(file_handler)

# -----------------------------
# Convenience Shortcuts
# -----------------------------
def get_logger(name: str = "app_logger"):
    """Get a logger instance"""
    return logging.getLogger(name)
