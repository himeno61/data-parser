import logging
import sys
import os

def setup_logger(name=__name__, log_level=None):
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    if logger.handlers:
        return logger
    
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(console_formatter)
    
    os.makedirs('logs', exist_ok=True)
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setLevel(logging.DEBUG)  # Always log DEBUG and above to file
    file_handler.setFormatter(file_formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler) 
    
    return logger

def get_logger(name=__name__):
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
