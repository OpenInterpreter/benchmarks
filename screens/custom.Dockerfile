FROM python:3.11.8

ARG USERNAME=gaia
ARG PASSWORD=1111

# Set environment variables to avoid user interaction prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update \
    && apt install -y --no-install-recommends \
       # An X server that stores the screen in memory.
       xvfb \
       # A VNC server that connects to the above X server.
       x11vnc \
       # A lightweight desktop environment built using Qt.
       lxqt \
       # Might be deprecated!  Maybe just install dbus??
       dbus-x11 \
       lightdm \
       sudo

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash ${USERNAME} \
    && echo "${USERNAME}:${PASSWORD}" | chpasswd \
    && adduser ${USERNAME} sudo

# Create a script to start all necessary services
COPY start.sh /home/${USERNAME}/start.sh
RUN chmod +x /home/${USERNAME}/start.sh

# Expose the VNC port
EXPOSE 5900

# # Switch to the new user
# USER ${USERNAME}
# WORKDIR /home/${USERNAME}

ENV DEFAULT_USER ${USERNAME}

# Entry point to start services
CMD /home/$DEFAULT_USER/start.sh
# ENTRYPOINT ["/bin/bash"]
