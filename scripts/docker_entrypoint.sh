
# Variables for simulator
ENV INSTANCE 0
ENV LAT 42.3898
ENV LON -71.1476
ENV ALT 14
ENV DIR 270
ENV MODEL +
ENV SPEEDUP 1
ENV VEHICLE ArduCopter
ENV PATH="/usr/local/bin:/root/.local/bin:${PATH}"

# Finally the command
ENV SITL_UDP_OUTPUT_ADDRESS udp:127.0.0.1:14550
ENTRYPOINT /ardupilot/Tools/autotest/sim_vehicle.py --vehicle ${VEHICLE} -I${INSTANCE} --custom-location=${LAT},${LON},${ALT},${DIR} -w --frame ${MODEL} --no-rebuild --speedup ${SPEEDUP} --out ${SITL_UDP_OUTPUT_ADDRESS}

