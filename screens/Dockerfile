FROM lscr.io/linuxserver/webtop:ubuntu-xfce

RUN apt update
RUN apt install git -y
RUN apt install python3-pip -y
RUN apt install python3-venv -y

COPY worker/ worker
RUN python3 -m venv .venv
RUN .venv/bin/python3 -m pip install -r worker/requirements.txt
# RUN python3 -m pip install -r worker/requirements.txt