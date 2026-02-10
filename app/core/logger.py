import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from app.core.config import settings

def setup_logging():
    # Create logs directory if it doesn't exist
    if not os.path.exists(settings.LOGS_DIR):
        os.makedirs(settings.LOGS_DIR)
        
    log_file = os.path.join(settings.LOGS_DIR, "app.log")
    
    # Create logger
    logger = logging.getLogger("Factify")
    logger.setLevel(logging.INFO)
    
    # detailed format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # File handler (writes to logs/app.log)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Console handler (writes to stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger

logger = setup_logging()
