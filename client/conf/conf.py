import logging
import os
import socket
import wave

import pyaudio
import yaml

# conf
c = {}
CONF_PATH = os.path.join(os.getcwd(), "conf.yml")


def get_host():
    global c
    if c["client"]["ip"]:
        return c["client"]["ip"]
    else:
        return socket.gethostbyname(socket.gethostname())


def get_port():
    global c
    if c["client"]["port"]:
        return int(c["client"]["port"])
    else:
        return 8001


def get_serial():
    global c
    return c["serial"]


def get_device_conf():
    global c
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


def get_ring_file_info():
    global c
    return c['rings'][c['phone_ring']]


def get_ring_play_stream():

    return play


def get_rings():
    global c
    return c['rings'].keys()


def set_rings(ring_name):
    global c
    c['phone_ring'] = ring_name
    return


class WavInfo:
    def __init__(self, voice_format, rate, chunk_size, channels):
        self.format = voice_format
        self.rate = rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.data = []


def init():
    global c
    with open(CONF_PATH, 'r', encoding="utf-8") as conf_f:
        c = yaml.load(conf_f.read(), yaml.FullLoader)
    # rings
    g = os.walk(os.path.join(os.getcwd(), "statics", "rings"))
    c['rings'] = {}
    p = pyaudio.PyAudio()
    for path, dir_list, file_list in g:
        for file_name in file_list:
            print(os.path.join(path, file_name))
            if file_name.endswith('.wav'):

                wf = wave.open(os.path.join(path, file_name), 'rb')
                voice_format = p.get_format_from_width(wf.getsampwidth())
                channels = wf.getnchannels()
                rate = wf.getframerate()
                chunk_size = 1024

                key = file_name.replace(".wav", "")
                c['rings'][key] = WavInfo(voice_format, rate, chunk_size, channels)

                data = wf.readframes(chunk_size)
                while len(data) > 0:
                    c['rings'][key].data.append(data)
                    data = wf.readframes(chunk_size)

    if c['phone_ring'] not in c['rings'].keys():
        logging.info("phone ring file is not exist:{}.wav".format(c['cur_ring']))
        exit(-1)
    return True
