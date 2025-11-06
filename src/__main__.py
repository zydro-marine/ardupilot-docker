from .logging import CustomFormatter
import logging
import time
import signal
import sys
from .sitl import SitlManager

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


if __name__ == "__main__":
    manager = SitlManager(ch)
    
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        manager.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    manager.start()

    try:
        last_status_log = 0
        while manager.is_running():
            time.sleep(1)
            if time.time() - last_status_log > 5:
                status = manager.get_status()
                running_count = sum(1 for v in status.values() if v)
                logger.info("SITL status: {}/{} instance(s) running".format(running_count, len(status)))
                last_status_log = time.time()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        manager.stop()