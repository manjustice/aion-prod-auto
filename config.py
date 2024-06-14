import logging
import os
from logging.handlers import RotatingFileHandler

PRODUCT_WINDOW_SIZE = (772, 555)
ITEMS_BLOCK_SIZE = (300, 420)
START_PRODUCTION_BUTTON = (86, 20)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# Logging settings
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = "bot.log"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file_path = os.path.join(LOG_DIR, LOG_FILE)

root_logger = logging.getLogger("bot")
root_logger.setLevel(logging.DEBUG)

fh_fastapi = RotatingFileHandler(log_file_path, maxBytes=1024 * 1024, backupCount=10)
fh_fastapi.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh_fastapi.setFormatter(formatter)
root_logger.addHandler(fh_fastapi)
