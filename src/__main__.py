from .logging import CustomFormatter
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


class SitlManager:
    def __init__(self):
        pass

    def start(self):
        logger.info("Starting SITL manager")
        pass

    def stop(self):
        logger.info("Stopping SITL manager")
        pass

    def is_running(self):
        pass


if __name__ == "__main__":
    manager = SitlManager()
    manager.start()

    while manager.is_running():
        time.sleep(1)

    manager.stop()
        