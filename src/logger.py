import os
import logging
from datetime import datetime

logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logger
def setup_logger():
   
    logger = logging.getLogger('fake_news_detection')
    logger.setLevel(logging.INFO)
    
    # Create file handler for logging to file
    log_file = os.path.join(logs_dir, 'prediction.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler for logging to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatter = logging.Formatter(f'%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create logger instance
logger = setup_logger()