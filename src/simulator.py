import logging
import subprocess
import os
import threading


class SimulatorInstance:
    # Manages a single simulator instance (ArduPilot + mavp2p)
    
    def __init__(self, instance_id, shared_env, logger_handler, log_dir):
        self.instance_id = instance_id
        self.sitl_process = None
        self.mavp2p_process = None
        self.shared_env = shared_env
        self.log_dir = log_dir
        self.instance_logger = logging.getLogger("instance_{}".format(instance_id))
        self.instance_logger.setLevel(logging.DEBUG)
        self.instance_logger.addHandler(logger_handler)

    def _forward_output(self, stream, process_name):
        for line in iter(stream.readline, ''):
            if line:
                self.instance_logger.info("[SITL {}][{}] {}".format(self.instance_id, process_name, line.rstrip()))

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
        env.setdefault('VEHICLE', 'Rover')
        env.setdefault('SITL_UDP_OUTPUT_ADDRESS', 'udp:127.0.0.1:{}'.format(14550 + self.instance_id))
        env['PATH'] = "/usr/local/bin:/root/.local/bin:{}".format(os.environ.get('PATH', ''))
        
        return env

    def start(self):
        self.instance_logger.info("Starting simulator instance {}".format(self.instance_id))
        
        env = self._build_env()

        instance_release_key = 'ARDUPILOT_INSTANCE_{}_RELEASE'.format(self.instance_id)
        release = os.environ.get(instance_release_key) or os.environ.get('ARDUPILOT_RELEASE')
        
        if release:
            sim_vehicle_path = '/home/ardupilot/builds/{}/Tools/autotest/sim_vehicle.py'.format(release)
        else:
            sim_vehicle_path = '/home/ardupilot/builds/Tools/autotest/sim_vehicle.py'

        sitl_cmd = [
            sim_vehicle_path,
            '--vehicle', env['VEHICLE'],
            "-I{}".format(env['INSTANCE']),
            "--custom-location={},{},{},{}".format(env['LAT'], env['LON'], env['ALT'], env['DIR']),
            '-w',
            '--frame', env['MODEL'],
            '--no-rebuild',
            '--speedup', env['SPEEDUP'],
            '--out', env['SITL_MAVLINK_OUTPUT_ADDRESS']
        ]

        mavp2p_input = env['SITL_MAVLINK_OUTPUT_ADDRESS'].replace('udp:', 'udpc:')
        mavp2p_input = env.get('MAVP2P_INPUT', 'udps:0.0.0.0:{}'.format(14550 + self.instance_id))
        
        instance_output_key = 'ARDUPILOT_INSTANCE_{}_MAVP2P_OUTPUT'.format(self.instance_id)
        mavp2p_output = os.environ.get(instance_output_key) or os.environ.get('ARDUPILOT_MAVP2P_OUTPUT', 'udp:127.0.0.1:{}'.format(14560 + self.instance_id))
        
        mavp2p_cmd = ['mavp2p', mavp2p_input, mavp2p_output]

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
            args=(self.sitl_process.stdout, 'SITL'),
            daemon=True
        ).start()
        threading.Thread(
            target=self._forward_output,
            args=(self.mavp2p_process.stdout, 'mavp2p'),
            daemon=True
        ).start()
        
        self.instance_logger.info("Simulator instance {} started".format(self.instance_id))

    def stop(self):
        self.instance_logger.info("Stopping simulator instance {}".format(self.instance_id))
        processes = [p for p in [self.sitl_process, self.mavp2p_process] if p]
        for process in processes:
            process.terminate()
        for process in processes:
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        self.instance_logger.info("Simulator instance {} stopped".format(self.instance_id))

    def is_running(self):
        sitl_running = self.sitl_process and self.sitl_process.poll() is None
        mavp2p_running = self.mavp2p_process and self.mavp2p_process.poll() is None
        return sitl_running or mavp2p_running

