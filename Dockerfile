FROM ardupilot/ardupilot-dev-base

# Setup environment config
ENV DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=jazzy
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV TZ=Etc/UTC
ENV ZYDRO_IS_IN_DOCKER=true
ENV TERM=xterm-color
ENV PIP_BREAK_SYSTEM_PACKAGES=1
ENV PYTHONUNBUFFERED=1
ARG COPTER_TAG=Copter-4.5.7

# Install base dependencies 
RUN apt-get update && \
    apt-get install -y \
    tzdata \
    sudo \
    lsb-release \
    git && \
    git config --global url."https://github.com/".insteadOf git://github.com/

# Create base folder structure
RUN mkdir -p /home/ardupilot
WORKDIR /home/ardupilot

# Install python dependencies
COPY ./requirements.txt ./requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Install mavp2p
RUN cd /home && \
    wget https://github.com/bluenviron/mavp2p/releases/download/v1.3.1/mavp2p_v1.3.1_linux_amd64.tar.gz && \
    tar -xvzf mavp2p_v1.3.1_linux_amd64.tar.gz && \
    mv mavp2p /usr/local/bin && \
    rm -rf mavp2p_v1.3.1_linux_amd64.tar.gz

# Clone ArduPilot
RUN git clone https://github.com/ArduPilot/ardupilot.git ardupilot-${COPTER_TAG} && \
    cd /home/ardupilot/ardupilot-${COPTER_TAG}  && \
    git checkout ${COPTER_TAG} && \
    git submodule update --init --recursive

# Build ArduPilot
RUN cd /home/ardupilot/ardupilot-${COPTER_TAG} && \
    ./waf distclean && \
    ./waf configure --board sitl && \
    ./waf copter

# Copy the management script
COPY ./src ./src

# Run management script
CMD ["python3", "-m", "src"]