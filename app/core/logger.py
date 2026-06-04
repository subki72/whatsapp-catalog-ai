import logging
import sys

def setup_logger():
    """
    Configures and returns a standard logger for the application.
    Logs are written to standard output.
    """
    logger = logging.getLogger("wa_catalog_bot")
    

    if not logger.handlers:
        logger.setLevel(logging.INFO)
        

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        ch.setFormatter(formatter)
        
        logger.addHandler(ch)
        
    return logger

logger = setup_logger()
