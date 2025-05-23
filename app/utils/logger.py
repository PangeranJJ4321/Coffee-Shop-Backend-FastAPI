import logging
import os
from logging.handlers import RotatingFileHandler

# Define log file path
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) # Set the logging level (INFO, DEBUG, WARNING, ERROR, CRITICAL)

# Create handlers
# Console handler
c_handler = logging.StreamHandler()
# File handler (for writing logs to a file, rotating at 5MB, keeping 5 backup files)
f_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5) # 5 MB per file

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)

# Example usage:
# logger.debug("This is a debug message")
# logger.info("This is an info message")
# logger.warning("This is a warning message")
# logger.error("This is an error message")
# logger.critical("This is a critical message")