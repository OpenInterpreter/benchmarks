FROM python:3.11.8

# Set environment variables to avoid user interaction prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       # An X server that stores the screen in memory.
       xvfb \
       # A VNC server that connects to the above X server.
       x11vnc \
       # A lightweight desktop environment built using Qt.
       lxqt \
       # Might be deprecated!  Maybe just install dbus??
       dbus-x11 \
       policykit-1 \
       lxqt-policykit \
       vim \
       xauth \
       sudo

RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a script to start all necessary services
COPY start22.sh /start.sh
RUN chmod +x /start.sh

# Expose the VNC port
EXPOSE 5900

# Entry point to start services
ENTRYPOINT ["/start.sh"]
