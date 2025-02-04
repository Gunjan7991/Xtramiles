import logging
import os
from logging.handlers import TimedRotatingFileHandler

# Define log directory as "log"
LOG_DIR = "logs"

# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Create Timed Rotating File Handler (New log file every day)
log_handler = TimedRotatingFileHandler(
    os.path.join(LOG_DIR, "app.log"), when="midnight", interval=1, backupCount=30
)
log_handler.suffix = "%Y-%m-%d"  # File format: app.log_YYYY-MM-DD
log_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
# logger.addHandler(logging.StreamHandler())  # Also log to console
