# utils/logging.py (Updated for Class Name)
import logging
from colorlog import ColoredFormatter
from config.config import GLOBAL_CONFIG

# Define a color code for light red (e.g., bright red foreground)
# Note: colorlog's 'red' is often bright enough. We'll use 'bold_red' for distinction.
CLASS_COLOR = GLOBAL_CONFIG.LOGGER_CLASS_COLOR

def setup_logger(name: str = "APP_MAIN"):
    """
    Initializes and returns a logger instance with a predefined, colored format.
    The log level is set dynamically using the GLOBAL_CONFIG.LOG_LEVEL.
    """
    logger = logging.getLogger(name)
    
    log_level = getattr(logging, GLOBAL_CONFIG.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    if logger.handlers:
        return logger
    
    # --- UPDATED LOG FORMAT ---
    # We use 'extra[class_name]' which will be supplied by the adapter below
    # The 'log_color' map handles the color application for the level and other fields
    log_format = (
        "%(white)s%(asctime)s%(reset)s | "
        "%(log_color)s%(levelname)-4s%(reset)s | "
        "[%(blue)s%(name)s%(reset)s] | "
        # Inject the class name field with its color
        f"(%({CLASS_COLOR})s%(class_name)s%(reset)s." 
        "(%(yellow)s%(funcName)s%(reset)s)) | "
        "%(message)s"
    )

    formatter = ColoredFormatter(
        log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red,bg_white',
            # Add the class color to the map for the custom field
            'bold_red': CLASS_COLOR 
        }
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level) 
    
    logger.addHandler(console_handler)

    return logger

class ClassLoggerAdapter(logging.LoggerAdapter):
    """
    Adapts a logger to automatically include the class name in the log record.
    """
    def process(self, msg, kwargs):
        # Inject the class name into the extra dict for use in the formatter
        kwargs["extra"] = {"class_name": self.extra["class_name"]}
        return msg, kwargs

def get_class_logger(module_name: str, class_name: str):
    """
    Gets a module logger and wraps it with an adapter to include the class name.
    
    Args:
        module_name (str): Typically __name__.
        class_name (str): The name of the class where the logger is initialized (e.g., self.__class__.__name__).
    """
    base_logger = setup_logger(module_name)
    # The dictionary passed here becomes self.extra in the adapter
    return ClassLoggerAdapter(base_logger, {"class_name": class_name})