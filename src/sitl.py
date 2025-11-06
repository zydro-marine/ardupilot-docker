import logging
import os
import time
from datetime import datetime
from .simulator import SimulatorInstance

logger = logging.getLogger(__name__)

class SitlManager:
    # Manages multiple simulator instances
    
    def __init__(self):
        self.instances = []
        self.running = False
        self.log_dir = None

    def _get_shared_env(self):
        shared_env = {}
        for key, value in os.environ.items():
            if key.startswith('ARDUPILOT_') and not key.startswith('ARDUPILOT_INSTANCE_'):
                env_key = key[len('ARDUPILOT_'):]
                if env_key != 'NUM_INSTANCES':
                    shared_env[env_key] = value
        return shared_env

    def start(self):
        num_instances = int(os.environ.get('ARDUPILOT_NUM_INSTANCES', '1'))
        logger.info("Starting {} SITL instances".format(num_instances))
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_dir = '/home/ardupilot/logs/{}'.format(timestamp)
        os.makedirs(self.log_dir, exist_ok=True)
        logger.info("Created log directory: {}".format(self.log_dir))
        
        shared_env = self._get_shared_env()
        
        for instance_id in range(num_instances):
            instance = SimulatorInstance(instance_id, shared_env, self.log_dir)
            instance.start()
            self.instances.append(instance)
            time.sleep(0.5)
        
        self.running = True
        logger.info("All {} SITL instances started".format(num_instances))

    def stop(self):
        if self.running or len(self.instances) > 0:
            logger.info("Stopping {} SITL instances".format(len(self.instances)))
            for instance in self.instances:
                instance.stop()
            self.instances.clear()
            self.running = False
            logger.info("All SITL instances stopped")

    def is_running(self):
        return any(instance.is_running() for instance in self.instances)
    
    def get_status(self):
        return {
            instance.instance_id: instance.is_running()
            for instance in self.instances
        }

