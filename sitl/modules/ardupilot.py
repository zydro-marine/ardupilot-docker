from sitl_sdk.modules.module_interface import ModuleInterface


class ArdupilotModule(ModuleInterface):
    name = "ardupilot"
    dependencies = []
    default_version = "local"

    def compose(self, version, ctx):
        if version == "local":
            image = "ardupilot-docker:local-{}".format(ctx.arch)
        elif version.startswith("local-"):
            image = "ardupilot-docker:{}".format(version[len("local-"):])
        else:
            image = "402590802363.dkr.ecr.us-east-2.amazonaws.com/ardupilot-docker:{}-{}".format(
                version, ctx.arch
            )

        cfg = ctx.config
        mav_port = cfg.get("mavlink_port", 14550)
        environment = {
            "ARDUPILOT_NUM_INSTANCES": "1",
            "ARDUPILOT_VEHICLE": cfg.get("vehicle", "APMrover2"),
            "ARDUPILOT_LAT": str(cfg.get("lat", 42.3898)),
            "ARDUPILOT_LON": str(cfg.get("lon", -71.1476)),
            "ARDUPILOT_ALT": str(cfg.get("alt", 0)),
            "ARDUPILOT_DIR": str(cfg.get("heading", 0)),
            "ARDUPILOT_SPEEDUP": str(cfg.get("speedup", 1)),
            "ARDUPILOT_SITL_MAVLINK_OUTPUT_ADDRESS": "udp:0.0.0.0:{}".format(mav_port),
        }
        if "release" in cfg:
            environment["ARDUPILOT_RELEASE"] = cfg["release"]

        return {
            "image": image,
            "environment": environment,
            "ports": ["{}/udp".format(mav_port)],
        }

    def client(self, ctx):
        return None
