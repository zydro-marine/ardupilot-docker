import logging
import time

class CustomFormatter(logging.Formatter):

    white = "\x1b[37;20m"
    cyan = "\x1b[36;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    base_format = "[%(asctime)s] [%(levelname)s] %(message)s"

    LEVEL_COLORS = {
        logging.DEBUG: cyan,
        logging.INFO: green,
        logging.WARNING: yellow,
        logging.ERROR: red,
        logging.CRITICAL: bold_red
    }

    def __init__(self):
        super().__init__(fmt=self.base_format)

    def formatTime(self, record, datefmt=None):
        return str(int(record.created * 1000))

    def format(self, record):
        level_color = self.LEVEL_COLORS.get(record.levelno, self.white)
        levelname_colored = "{}{}{}".format(level_color, record.levelname, self.reset)
        
        original_levelname = record.levelname
        record.levelname = levelname_colored
        
        formatted = super().format(record)
        
        record.levelname = original_levelname
        
        return "{}{}{}".format(self.white, formatted, self.reset)
