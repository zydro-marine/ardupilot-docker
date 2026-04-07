# ardupilot-docker

A Docker container for running SITL testing of ArduPilot drones. 

This container wraps ArduPilot in a test harness which adds a number of advanced features, including environment-variable based configuration, multiple isolated simulation instances & mavp2p mavlink forwarding.

> Note: The use case at Zydro Marine for this container is to test integrations _against_ ArduPilot (eg. our Mavlink interfaces & C2 software), so we've made ergonomics decisions to make it easier to spin up/down "throwaway" ArduPilot instances. If you are actively developing against ArduPilot, you are better off directly using the ArduPilot SITL system.

## Features

- Run multiple independent ArduPilot SITL instances with independent configurations from a single docker container
- Select specific ArduPilot releases per instance (e.g., `Rover-4.6.3`, `ArduCopter-4.5.0`)
- Creates timestamped log directories for each session at `/ardupilot/logs/<timestamp>`
- Integrated mavp2p Mavlink forwarding

## Usage

Configuration of the simulation is done via environment variables, set in the `docker-compose.yml` file or via flags to the Docker CLI.

### Basic Usage

Start a single ArduPilot SITL instance using docker-compose:

```bash
docker-compose up
```

The container will automatically:

- Start ArduPilot SITL and mavp2p and forward all output to the console
- Create a timestamped log directory at `/ardupilot/logs/<timestamp>` (e.g., `/ardupilot/logs/20241215_143022`)

### Environment Variable Configuration

Configuration is done through environment variables.

#### Manager Config

These variables control the behavior of the SITL launcher.

- `ARDUPILOT_NUM_INSTANCES` - Number of simulator instances to spawn (default: `1`)

#### Shared Config

Prefix with `ARDUPILOT_`:

- `ARDUPILOT_RELEASE` - ArduPilot release tag to use (e.g., `Rover-4.6.3`).
- `ARDUPILOT_VEHICLE` - ArduPilot vehicle type (default: `Rover`)
- `ARDUPILOT_LAT` - Starting latitude (default: `42.3898`)
- `ARDUPILOT_LON` - Starting longitude (default: `-71.1476`)
- `ARDUPILOT_ALT` - Starting altitude (default: `0`)
- `ARDUPILOT_DIR` - Starting heading (default: `0`)
- `ARDUPILOT_MODEL` - Frame/model type (default: `+`)
- `ARDUPILOT_SPEEDUP` - Simulation speedup factor (default: `1`)
- `ARDUPILOT_SITL_MAVLINK_OUTPUT_ADDRESS` - MAVLink output address (default: `udp:127.0.0.1:14550` for instance 0)
- `ARDUPILOT_MAVP2P_OUTPUT` - mavp2p output address (default: `udp:127.0.0.1:14560` for instance 0)

#### Instance-Specific Config

Prefix with `ARDUPILOT_INSTANCE_<X>_` where `<X>` is the instance ID (0, 1, 2, etc.):

- `ARDUPILOT_INSTANCE_<X>_RELEASE` - ArduPilot release tag for this specific instance
- `ARDUPILOT_INSTANCE_<X>_VEHICLE` - Vehicle type for this instance
- `ARDUPILOT_INSTANCE_<X>_LAT` - Starting latitude for this instance
- `ARDUPILOT_INSTANCE_<X>_LON` - Starting longitude for this instance
- `ARDUPILOT_INSTANCE_<X>_ALT` - Starting altitude for this instance
- `ARDUPILOT_INSTANCE_<X>_DIR` - Starting heading for this instance
- `ARDUPILOT_INSTANCE_<X>_MODEL` - Frame/model type for this instance
- `ARDUPILOT_INSTANCE_<X>_SPEEDUP` - Simulation speedup for this instance
- `ARDUPILOT_INSTANCE_<X>_SITL_MAVLINK_OUTPUT_ADDRESS` - MAVLink output address for this instance
- `ARDUPILOT_INSTANCE_<X>_MAVP2P_OUTPUT` - mavp2p output address for this instance

Instance-specific variables override global variables for that instance. If not specified, instances use defaults based on their instance ID (e.g., port numbers increment: instance 0 uses port 14550, instance 1 uses 14551, etc.).

### Spinning up Multiple Instances

To run multiple simulator instances, set `ARDUPILOT_NUM_INSTANCES`:

```yaml
environment:
  ARDUPILOT_NUM_INSTANCES: 3
```

Each instance will:
- Use incrementing port numbers (instance 0: 14550, instance 1: 14551, etc.)
- Have its own log output prefixed with `[SITL <id>]`
- Can be configured independently using instance-specific environment variables

Example with different configurations per instance:

```yaml
environment:
  ARDUPILOT_NUM_INSTANCES: 2
  ARDUPILOT_VEHICLE: ArduCopter
  ARDUPILOT_INSTANCE_0_VEHICLE: ArduCopter
  ARDUPILOT_INSTANCE_0_LAT: 42.3898
  ARDUPILOT_INSTANCE_0_LON: -71.1476
  ARDUPILOT_INSTANCE_1_VEHICLE: Rover
  ARDUPILOT_INSTANCE_1_LAT: 42.3900
  ARDUPILOT_INSTANCE_1_LON: -71.1478
```

### Selecting ArduPilot Release

To use a specific ArduPilot release, set the `ARDUPILOT_RELEASE` environment variable:

```yaml
environment:
  ARDUPILOT_RELEASE: Rover-4.6.3
```

This will use `/ardupilot/builds/Rover-4.6.3/Tools/autotest/sim_vehicle.py`.

You can also specify different releases per instance:

```yaml
environment:
  ARDUPILOT_NUM_INSTANCES: 2
  ARDUPILOT_RELEASE: Rover-4.6.3
  ARDUPILOT_INSTANCE_0_RELEASE: Rover-4.6.3
  ARDUPILOT_INSTANCE_1_RELEASE: ArduCopter-4.5.0
```

### Log Directory

The SITL Manager automatically creates a timestamped log directory at `/ardupilot/logs/<timestamp>` (format: `YYYYMMDD_HHMMSS`) when it starts. All programs (ArduPilot SITL and mavp2p) run with this directory as their working directory, so any files they create (logs, data files, etc.) will be saved there.

### MAVP2P Configuration

mavp2p is automatically started for each instance to allow multiple MAVLink connections. By default:
- Input: Connects to the SITL MAVLink output
- Output: `udp:127.0.0.1:14560` (for instance 0, incrementing for additional instances)

You can customize the mavp2p output using `ARDUPILOT_MAVP2P_OUTPUT` or `ARDUPILOT_INSTANCE_<X>_MAVP2P_OUTPUT`.

## Developer Setup

TODO
