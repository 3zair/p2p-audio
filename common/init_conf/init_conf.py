import os.path
import socket

import pyaudio
import yaml
from serial.tools import list_ports

if __name__ == '__main__':
    ports = list(list_ports.comports())
    if len(ports) <= 0:
        print("错误：未插入接线盒")
        exit(-1)
    if not os.path.exists("conf.yml"):
        # 初始化客户端配置，此时不许插入听筒
        content = {
            "client": {
                "ip": socket.gethostbyname(socket.gethostname()),
                "port": 8001
            },
            "serial": "",
            "device": {},
            "phone_ring": "经典1"
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

        for i in range(len(ports)):
            name = ports[i].name
            if name.find("CH340"):
                content['serial'] = name
        with open("conf.yml", "w", encoding="utf-8") as yaml_file:
            yaml.dump(content, yaml_file, allow_unicode=True)
    else:
        # 插入听筒后运行
        with open("conf.yml", "r", encoding="utf-8") as yaml_file:
            # yaml.dump(content, yaml_file, allow_unicode=True)
            content = yaml.load(yaml_file, Loader=yaml.FullLoader)
            print(content)
            device = content["device"]
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            for i in range(0, num_devices):
                name = p.get_device_info_by_host_api_device_index(0, i).get('name')
                if not name.endswith(")"):
                    name += ")"
                if name.startswith("扬声器") and name.find("USB") > 0:
                    n = name[len("扬声器 ("):len(name) - 1]
                    if n not in device["headset"] and n not in device["phone"]:
                        content["device"]["phone"].append(name[len("扬声器 ("):len(name) - 1])

            with open("conf.yml", "w", encoding="utf-8") as yf:
                yaml.dump(content, yf, allow_unicode=True)
