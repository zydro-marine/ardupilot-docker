import socket

from sitl_sdk.fixtures import world


def test_mavlink_port_reachable(world):
    """ArduPilot's MAVLink UDP port is published on the host."""
    node = world.node("ardupilot1")
    assert node.host is not None
    assert node.port is not None

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(1.0)
        sock.sendto(b"", (node.host, node.port))
    finally:
        sock.close()
