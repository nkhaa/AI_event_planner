import logging
from datetime import datetime
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_file = f"{log_dir}/app_{datetime.now().strftime('%Y%m%d')}.log"

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.ERROR)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)
