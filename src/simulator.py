import logging
import subprocess
import os
import sys
import threading

logger = logging.getLogger(__name__)

class SimulatorInstance:
    # Manages a single simulator instance (ArduPilot + mavp2p)
    
    def __init__(self, instance_id, shared_env, log_dir):
        self.instance_id = instance_id
        self.sitl_process = None
        self.mavp2p_process = None
        self.shared_env = shared_env
        self.log_dir = log_dir

    def _forward_output(self, stream, process_name):
        for line in iter(stream.readline, ''):
            if line:
                logger.info("[SITL {}] [{}] {}".format(self.instance_id, process_name, line.rstrip()))

    def _build_env(self):
        env = self.shared_env.copy()
        
        instance_prefix = 'ARDUPILOT_INSTANCE_{}_'.format(self.instance_id)
        for key, value in os.environ.items():
            if key.startswith(instance_prefix):
                env_key = key[len(instance_prefix):]
                env[env_key] = value
        
        env['INSTANCE'] = str(self.instance_id)
        
        env.setdefault('LAT', '42.3898')
        env.setdefault('LON', '-71.1476')
        env.setdefault('ALT', '0')
        env.setdefault('DIR', '0')
        env.setdefault('MODEL', '+')
        env.setdefault('SPEEDUP', '1')
        env.setdefault('VEHICLE', 'APMrover2')

        self.output_udp_address = 'udp:127.0.0.1:{}'.format(14550 + self.instance_id)
        self.output_port = 14550 + self.instance_id

        env['PATH'] = "/usr/local/bin:/root/.local/bin:{}".format(os.environ.get('PATH', ''))
        
        return env

    def start(self):
        logger.info("Starting simulator instance {}".format(self.instance_id))
        
        env = self._build_env()

        instance_release_key = 'ARDUPILOT_INSTANCE_{}_RELEASE'.format(self.instance_id)
        release = os.environ.get(instance_release_key) or os.environ.get('ARDUPILOT_RELEASE')
        
        if not release:
            builds_dir = '/home/ardupilot/builds'
            if os.path.exists(builds_dir):
                releases = [d for d in os.listdir(builds_dir) if os.path.isdir(os.path.join(builds_dir, d))]
                if releases:
                    releases.sort()
                    release = releases[0]
                    logger.info("No release specified, using first available: {}".format(release))
                else:
                    logger.error("No ArduPilot release found in {} and no release specified via ARDUPILOT_RELEASE or ARDUPILOT_INSTANCE_{}_RELEASE".format(builds_dir, self.instance_id))
                    sys.exit(1)
            else:
                logger.error("ArduPilot builds directory {} does not exist and no release specified via ARDUPILOT_RELEASE or ARDUPILOT_INSTANCE_{}_RELEASE".format(builds_dir, self.instance_id))
                sys.exit(1)
        
        sim_vehicle_path = '/home/ardupilot/builds/{}/Tools/autotest/sim_vehicle.py'.format(release)
        if not os.path.exists(sim_vehicle_path):
            logger.error("ArduPilot release '{}' not found at {}".format(release, sim_vehicle_path))
            sys.exit(1)

        sitl_cmd = [
            sim_vehicle_path,
            '--vehicle', env['VEHICLE'],
            "-I{}".format(env['INSTANCE']),
            "--custom-location={},{},{},{}".format(env['LAT'], env['LON'], env['ALT'], env['DIR']),
            '-w',
            '--frame', env['MODEL'],
            '--speedup', env['SPEEDUP'],
            '--no-rebuild',
            '--no-mavproxy',
        ]

        mavlink_input_port = 5760 + self.instance_id

        mavp2p_input = self.output_udp_address.replace('udp:', 'udpc:')
        mavp2p_udp_port = os.environ.get('ARDUPILOT_INSTANCE_{}_MAVP2P_UDP_OUTPUT_PORT'.format(self.instance_id)) or os.environ.get('ARDUPILOT_MAVP2P_UDP_OUTPUT_PORT', 5600 + self.instance_id)
        mavp2p_tcp_port = os.environ.get('ARDUPILOT_INSTANCE_{}_MAVP2P_TCP_OUTPUT_PORT'.format(self.instance_id)) or os.environ.get('ARDUPILOT_MAVP2P_TCP_OUTPUT_PORT', 5601 + self.instance_id)
        
        mavp2p_cmd = ['mavp2p', 'tcpc:127.0.0.1:{}'.format(mavlink_input_port), 'udps:0.0.0.0:{}'.format(mavp2p_udp_port), 'tcps:0.0.0.0:{}'.format(mavp2p_tcp_port)]
        logger.info("Starting mavp2p with command: {}".format(' '.join(mavp2p_cmd)))
        logger.info("Starting sitl with command: {}".format(' '.join(sitl_cmd)))

        self.sitl_process = subprocess.Popen(
            sitl_cmd,
            env=env,
            cwd=self.log_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        self.mavp2p_process = subprocess.Popen(
            mavp2p_cmd,
            cwd=self.log_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        threading.Thread(
            target=self._forward_output,
            args=(self.sitl_process.stdout, 'ardupilot'),
            daemon=True
        ).start()
        threading.Thread(
            target=self._forward_output,
            args=(self.mavp2p_process.stdout, 'mavp2p'),
            daemon=True
        ).start()
        
        logger.info("Simulator instance {} started".format(self.instance_id))

    def stop(self):
        logger.info("Stopping simulator instance {}".format(self.instance_id))
        processes = [p for p in [self.sitl_process, self.mavp2p_process] if p]
        for process in processes:
            process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        logger.info("Simulator instance {} stopped".format(self.instance_id))

    def is_running(self):
        sitl_running = self.sitl_process and self.sitl_process.poll() is None
        mavp2p_running = self.mavp2p_process and self.mavp2p_process.poll() is None
        return sitl_running or mavp2p_running

