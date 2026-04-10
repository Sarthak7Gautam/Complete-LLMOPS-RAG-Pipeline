import os 
import logging 
from datetime import datetime
import structlog

# This is a boilerplate code you dont need to remember it
class CustomLogger:
    def __init__(self,log_dir = 'logs'):
        self.logs_dir = os.path.join(os.getcwd(),log_dir)
        os.makedirs(self.logs_dir,exist_ok=True)

        log_file = f"{datetime.now().strftime("%d/%m/%Y_%H:%M:%S")}.log"
        self.log_file_path = os.path.join(os.getcwd(),log_file)

    def get_logger(self, name=__file__): # creates a logger function which initializes the name to the script in which you are running this code
        logger_name = os.path.basename(name) # cleans the file name into just app.py or main.py

        file_handler = logging.FileHandler(self.log_file_path) # tells the system where to log on hard drive
        file_handler.setLevel(logging.INFO) # filter for the file and recording anything labelled INFO or more important
        file_handler.setFormatter(logging.Formatter("%(message)s")) # determines how the text looks like here its just raw message

        console_handler = logging.StreamHandler() # tells the system to also add logs to your terminal/screen
        console_handler.setLevel(logging.INFO) # filter for the file and recording anything labelled INFO or more important
        console_handler.setFormatter(logging.Formatter("%(message)s")) # determines how the text looks like here its just raw message

        logging.basicConfig( # This "marries" the file and screen settings together into the standard Python logging system.
            level=logging.INFO,
            format="%(message)s",
            handlers=[console_handler, file_handler]
        )

        structlog.configure( # This is the "brain." It wraps around the standard logger to add extra features.
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),# Tells structlog to use Python’s built-in logging system as its foundation.
            cache_logger_on_first_use=True, # An efficiency boost so the system doesn't have to re-configure itself every time you log something.
        )

        return structlog.get_logger(logger_name) # Hands you the finished "logger tool" so you can start typing logger.info("Hello!")
