#!/bin/bash

# Set environment variable for lxqt
export XDG_RUNTIME_DIR=/run/user/$(id -u)
mkdir -p $XDG_RUNTIME_DIR
chmod 0700 $XDG_RUNTIME_DIR

# Start Xvfb on display :1
Xvfb :1 -screen 0 1024x768x24 &

# Wait for Xvfb to start
sleep 2

# Set the DISPLAY environment variable
export DISPLAY=:1

service dbus start

# Start the LXQt desktop environment
startlxqt &

# Wait for LXQt to start
sleep 2

# Start x11vnc
x11vnc -display :1 -passwd yourpassword -forever -nopw &
X11VNC_PID=$!

# Wait to keep the container running
wait