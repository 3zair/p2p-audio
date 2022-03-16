import socket

import pyaudio
import yaml

if __name__ == '__main__':
    content = {
        "client": {
            "ip": socket.gethostbyname(socket.gethostname()),
            "port": 8001
        },
        "serial": "",
        "device": {},
        "storage": {
            "root": "C:\\"
        }
    }

    device = {
        "headset": [],
        "default": [],
        "phone": []
    }
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    for i in range(0, num_devices):
        name = p.get_device_info_by_host_api_device_index(0, i).get('name')
        if not name.endswith(")"):
            name += ")"
        if name.startswith("扬声器"):
            if name.find("USB") > 0:
                device["headset"].append(name[len("扬声器 ("):len(name) - 1])
            else:
                device["default"].append(name[len("扬声器 ("):len(name) - 1])
    content["device"] = device
    with open("./conf.yml", "w", encoding="utf-8") as yaml_file:
        yaml.dump(content, yaml_file, allow_unicode=True)
