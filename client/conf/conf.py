import os
import socket
import yaml

# conf
c = {}
CONF_PATH = os.path.join(os.getcwd(), "conf.yml")


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


def get_device_conf():
    ret = {
        "headset_input": [],
        "headset_output": [],
        "default_output": [],
        "phone_output": [],
        "phone_input": [],
    }
    for hs in c['device']['headset']:
        ret["headset_input"].append("麦克风 ({})".format(hs))
        ret["headset_output"].append("扬声器 ({})".format(hs))
    for ho in c['device']['default']:
        ret["default_output"].append("扬声器 ({})".format(ho))
    for phone in c['device']['phone']:
        ret["phone_input"].append("麦克风 ({})".format(phone))
        ret["phone_output"].append("扬声器 ({})".format(phone))
    print(ret)
    return ret


def get_storage_dir():
    return c["storage"]['root']


def init():
    global c
    with open(CONF_PATH, 'r', encoding="utf-8") as conf_f:
        c = yaml.load(conf_f.read(), yaml.FullLoader)

    if not os.path.exists(c["storage"]['root']):
        os.mkdir(c["storage"]['root'])
    return True
