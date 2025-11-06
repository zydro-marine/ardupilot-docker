from .logging import CustomFormatter
import logging
import time
import signal
import sys
from .sitl import SitlManager

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

# Remove any existing handlers to avoid duplicates
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Create and add a single handler with our formatter
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
root_logger.addHandler(ch)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    manager = SitlManager()
    
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