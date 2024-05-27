#!/bin/bash

# Set environment variable for lxqt
export XDG_RUNTIME_DIR=/run/user/$(id -u)
mkdir -p $XDG_RUNTIME_DIR
chmod 0700 $XDG_RUNTIME_DIR

# Start Xvfb
Xvfb :0 -screen 0 1024x768x24 &
export DISPLAY=:0

# Wait for Xvfb to start
sleep 2

# Create .Xauthority file
export XAUTHORITY=$XDG_RUNTIME_DIR/.Xauthority
touch $XAUTHORITY
xauth generate :0 . trusted
xauth add :0 . $(xauth list :0 | tail -n 1 | awk '{print $3}')

# Run everything within a dbus-run-session
dbus-run-session -- bash <<EOF
  # Start lxqt-policykit-agent
  lxqt-policykit-agent &

  # Start lxqt-session via startlxqt
  startlxqt &

  # Wait for lxqt-session to start
  sleep 2

  # Start x11vnc with password
  x11vnc -storepasswd 1111 /etc/x11vnc.pass
  x11vnc -display :0 -forever -rfbauth /etc/x11vnc.pass -create &
  wait
EOF
