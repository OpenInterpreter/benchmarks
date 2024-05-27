#!/bin/bash

# Set environment variable for lxqt
export XDG_RUNTIME_DIR=/run/user/$(id -u)
mkdir -p $XDG_RUNTIME_DIR
chmod 0700 $XDG_RUNTIME_DIR

# Start dbus
dbus-daemon --system --fork

# Wait for dbus to be ready
echo "Waiting for dbus to start..."
while ! dbus-send --system --dest=org.freedesktop.DBus --type=method_call --print-reply /org/freedesktop/DBus org.freedesktop.DBus.ListNames > /dev/null 2>&1; do
  sleep 1
done
echo "dbus is ready."

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

# Start lxpolkit (PolicyKit authentication agent)
lxqt-policykit-agent &
sleep 2

# Start lxqt-session via startlxqt
startlxqt &
sleep 2

# Start x11vnc
x11vnc -storepasswd 1111 /etc/x11vnc.pass
x11vnc -display :0 -forever -rfbauth /etc/x11vnc.pass -create &
wait
