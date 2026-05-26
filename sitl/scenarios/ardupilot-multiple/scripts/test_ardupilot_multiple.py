import socket

import pytest

from sitl_sdk.fixtures import world


@pytest.mark.parametrize("name", ["ardupilot1", "ardupilot2", "ardupilot3", "ardupilot4"])
def test_mavlink_port_reachable(world, name):
    node = world.node(name)
    assert node.host is not None
    assert node.port is not None

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(1.0)
        sock.sendto(b"", (node.host, node.port))
    finally:
        sock.close()
