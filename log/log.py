import logging,os
from logging.handlers import TimedRotatingFileHandler

LOG_DIR=os.path.join(os.path.dirname(__file__),"../log")
os.makedirs(LOG_DIR,exist_ok=True)


LOG_FILE=os.path.join(LOG_DIR,"assistant.log")


logger=logging.getLogger("assistant")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    file_handler=TimedRotatingFileHandler(
        LOG_FILE,when="midnight",interval=1,backupCount=7,encoding="utf-8"
    )
    file_handler.setLevel(logging.INFO)

    console_handler=logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter=logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(threadName)s] — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def get_logger():
    return logger