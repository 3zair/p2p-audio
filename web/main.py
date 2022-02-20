# 暂时没用
from flask import Flask, request, jsonify
from common import mgo

app = Flask(__name__)

Channels = mgo.getChannels()
Clients = mgo.getClients()


# 判断channel是否可用
@app.route("/channel/occupy", methods=['POST'])
def hello_world():
    channel_id = request.form.get("channel_id")
    uid = request.args.get("uid")
    if "user" not in Channels["channel_id"]:
        Channels["channel_id"]["user"] = uid
        return jsonify({"code": 200, "msg": "信道占用成功"})
    elif Clients[Channels["channel_id"]["user"]]["level"] < Clients["uid"]["level"]:
        pass
    else:
        return jsonify({"code": 201, "msg": "已被更高等级用户占用", "cur_id": Channels["channel_id"]["user"]})


import serial
import time

portx = "COM3"
bps = 9600
ser = serial.Serial(None, bps, rtscts=True, dsrdtr=True)

def rec_tra():
    ser.setPort(portx)
    ser.dtr = True
    ser.open()
    while True:
        for i in range(0, 100):
            i += 1
            print(i, " DTR:", ser.dtr, " CD:", ser.cd, " DSR:", ser.dsr, " CTS:", ser.cts)
            time.sleep(0.22)


if __name__ == '__main__':
    try:
        rec_tra()
    except KeyboardInterrupt:
        if ser is not None:
            ser.close()


import pyaudio
import wave

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
num_devices = info.get('deviceCount')
for i in range(0, num_devices):
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
        print("input device id ", i, "-", p.get_device_info_by_host_api_device_index(0, i).get('name'))
    if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
        print("output device id ", i, "-", p.get_device_info_by_host_api_device_index(0, i).get('name'))
"""
input device id  0 - Microsoft 声音映射器 - Input
input device id  1 - 麦克风 (2- USB Audio Device)
input device id  2 - 麦克风 (USB Audio Device)
output device id  3 - Microsoft 声音映射器 - Output
output device id  4 - 扬声器 (2- USB Audio Device)
output device id  5 - Digital Audio (S/PDIF) (2- High
output device id  6 - 扬声器 (2- High Definition Audio D
output device id  7 - 扬声器 (USB Audio Device)
output device id  8 - LG ULTRAGEAR (NVIDIA High Defin
"""
#
# def get_audio_devices():
#     p = pyaudio.PyAudio()
#     devices = []
#     for i in range(p.get_device_count()):
#         devices.append(p.get_device_info_by_index(i))
#     return devices
#
#
# def get_audio_input_devices():
#     devices = []
#     for item in get_audio_devices():
#         if item.get('maxInputChannels') > 0:
#             devices.append(item)
#     return devices
#
#
# def get_audio_output_devices():
#     devices = []
#     for item in get_audio_devices():
#         if item.get('maxOutputChannels') > 0:
#             devices.append(item)
#     return devices
#
#
# if __name__ == '__main__':
#     print("input devices:")
#     for item in get_audio_input_devices():
#         print(item.get('name'))
#     print("-------------------------")
#     print("output devices:")
#     for item in get_audio_output_devices():
#         print(item.get('name'))

chunk = 1024
f = wave.open("./temp/input300.wav", "rb")
p = pyaudio.PyAudio()


def audioFunc1():
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=f.getframerate(),
                    output=True,
                    output_device_index=4)
    data = f.readframes(chunk)
    while len(data) > 0:
        stream.write(data)
        data = f.readframes(chunk)


def audioFunc2():
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=f.getframerate(),
                    output=True,
                    output_device_index=7)
    data = f.readframes(chunk)
    while len(data) > 0:
        stream.write(data)
        data = f.readframes(chunk)


# if __name__ == '__main__':
#     Thread(target=audioFunc1).start()
#     Thread(target=audioFunc2).start()