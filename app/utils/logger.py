import logging
import os
from datetime import datetime

def setup_logger(name, log_level):
    # Map string values to their equivalent logging levels
    level_map = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING,
                 'ERROR': logging.ERROR, 'CRITICAL': logging.CRITICAL}
    
    # Get Flask's built-in logger
    logger = logging.getLogger(name)
    
    # Set the log level based on the mapping
    logger.setLevel(level_map.get(log_level, logging.DEBUG))
    
    return logger
