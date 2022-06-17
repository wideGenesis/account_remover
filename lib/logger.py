import logging
import os
from logging.handlers import RotatingFileHandler
# import sys
# from azure.identity import DefaultAzureCredential
# from azure.storage.blob import BlobClient
import project_settings
from project_settings import LOG_TO_FILE, LOGGER_LEVEL, IS_LOCAL_ENV

DEBUG_LOG_FILE = None


class BColors:
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    BLUE = '\033[34m'
    CYAN = '\033[36m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_RED = '\033[91m'
    LIGHT_GREY = '\033[37m'

    def disable(self):
        self.RED = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.BLUE = ''
        self.CYAN = ''
        self.LIGHT_GREEN = ''
        self.LIGHT_RED = ''
        self.LIGHT_GREY = ''


class ColorHandler(logging.StreamHandler):
    COLORS = {
        logging.DEBUG: BColors.CYAN,
        logging.INFO: BColors.LIGHT_GREY,
        logging.WARNING: BColors.YELLOW,
        logging.ERROR: BColors.LIGHT_RED,
        logging.CRITICAL: BColors.RED
    }

    def emit(self, record: logging.LogRecord) -> None:
        color = self.COLORS.get(record.levelno, '')
        self.stream.write(color + self.format(record) + '\n')


class CustomLogger:
    LOG_FILE_PATH = project_settings.LOG_FILE_PATH
    logger = None

    @classmethod
    def get_logger(cls, service_name='django'):
        if cls.logger is not None:
            return cls.logger

        stdout_handler = ColorHandler()
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)-3s] - FILE: %(module)-3s - FUNC: %('
            'funcName)-3s - [LINE: %(lineno)-3s] >>> %(message)s '
        )

        cls.logger = logging.getLogger(service_name)
        if not cls.logger.hasHandlers():
            if int(LOG_TO_FILE):
                file_handler = RotatingFileHandler(cls.LOG_FILE_PATH, maxBytes=50000, backupCount=20)
                cls.logger.addHandler(file_handler)
                file_handler.setFormatter(formatter)
                cls.logger.addHandler(stdout_handler)
                stdout_handler.setFormatter(formatter)
            else:
                cls.logger.addHandler(stdout_handler)
                stdout_handler.setFormatter(formatter)
            cls.logger.setLevel(LOGGER_LEVEL)
            return cls.logger
        else:
            cls.logger.removeHandler(stdout_handler)



#
#
# logger = logging.getLogger('azure')
# logger.setLevel(logging.DEBUG)
#
# # Set the logging level for the azure.storage.blob library
# logger = logging.getLogger('azure.storage.blob')
# logger.setLevel(logging.DEBUG)
#
# # Direct logging output to stdout. Without adding a handler,
# # no logging output is visible.
# handler = logging.StreamHandler(stream=sys.stdout)
# logger.addHandler(handler)
#
# credential = DefaultAzureCredential()
# storage_url = os.environ["AZURE_STORAGE_BLOB_URL"]
#
# # Enable logging on the client object
# blob_client = BlobClient(storage_url, container_name="blob-container-01",
#     blob_name="sample-blob9.txt", credential=credential)
#
# with open("./sample-source.txt", "rb") as data:
#     blob_client.upload_blob(data, logging_enable=True)