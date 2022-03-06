import os
import socket
import yaml

# conf
c = {}
CONF_PATH = os.path.join(os.getcwd(), "conf.yaml")


def get_host():
    if c["client"]["ip"]:
        return c["client"]["ip"]
    else:
        return socket.gethostbyname(socket.gethostname())


def get_port():
    if c["client"]["port"]:
        return int(c["client"]["port"])
    else:
        return 8001


def get_serial():
    return c["serial"]


def init():
    global c
    with open(CONF_PATH, 'r', encoding="utf-8") as conf_f:
        c = yaml.load(conf_f.read(), yaml.FullLoader)
    return True
