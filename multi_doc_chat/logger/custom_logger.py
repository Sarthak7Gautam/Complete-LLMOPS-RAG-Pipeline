import os 
import logging 
from datetime import datetime
import structlog
from multi_doc_chat.exceptions import custom_exception

# Ensure structlog is configured only once at module load
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# This is a boilerplate code you dont need to remember it
class CustomLogger:
    def __init__(self,log_dir = 'logs'):
        try:
            self.logs_dir = os.path.join(os.getcwd(),log_dir)
            os.makedirs(self.logs_dir,exist_ok=True)

            log_file = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
            self.log_file_path = os.path.join(self.logs_dir,log_file)
        except  Exception as e:
            raise custom_exception.DocumentPortalException(e)

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

        return structlog.get_logger(logger_name) # Hands you the finished "logger tool" so you can start typing logger.info("Hello!")
