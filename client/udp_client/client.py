import time
import socket
import threading
import logging
import json
import random

import numpy as np
import pyaudio
import serial

import conf.conf as conf
from math import sqrt
from queue import Queue

from .my_udp import UdpMsg
from common.mgo import col_user, col_channel

from .volume_control_utils import MyAudioUtilities
from comtypes import CLSCTX_ALL
from pycaw.pycaw import IAudioEndpointVolume, AudioDeviceState
from ctypes import POINTER, cast

speaking_channels = set()
speaking_users = set()


def get_speaking_channels():
    global speaking_channels
    return speaking_channels


def get_speaking_users():
    global speaking_users
    return speaking_users


def pop_speaking_channels():
    global speaking_channels
    if len(speaking_channels) > 0:
        return speaking_channels.pop()
    else:
        return None


def pop_speaking_users():
    global speaking_users
    if len(speaking_users):
        return speaking_users.pop()
    else:
        return None


# 控制音量
OutputDevices = {
    "pc": [],
    "usb": [],
}


def init_output_device_volume():
    global OutputDevices
    # 打印所有音频设备
    device_list = MyAudioUtilities.GetAllDevices()
    i = 0
    for device in device_list:
        if device.state == AudioDeviceState.Active:
            if device.FriendlyName.find("扬声器") >= 0:
                # 设置音量
                try:
                    tmp = device.id
                    devices = MyAudioUtilities.GetDevice(tmp)
                    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                    volume = cast(interface, POINTER(IAudioEndpointVolume))
                    volume.SetMasterVolumeLevelScalar(100, None)
                except Exception as e:
                    logging.warning("set_output_volume_value err:{}".format(e))
        i += 1


class OutputConf:
    def __init__(self, cur_output=2, pc=70, usb=70):
        self.output_device = cur_output
        self.volume = usb  # 当前所选设备的音量
        self.pc = pc
        self.usb = usb


# 通道的输出设备相关配置
# key: ${channel_id}, phone_call
# value: OutputConf
OutputVolumeConf = {
    "phone": OutputConf(cur_output=2, pc=0, usb=70)
}

CurChannel = None


# 修改音量
def change_channel_output_volume(channel_id, usb_volume=-1, pc_volume=-1):
    global OutputVolumeConf
    if channel_id in OutputVolumeConf:
        if not pc_volume == -1:
            OutputVolumeConf[channel_id].pc = pc_volume
            if OutputVolumeConf[channel_id].output_device == 1:
                OutputVolumeConf[channel_id].volume = pc_volume
        if not usb_volume == -1:
            OutputVolumeConf[channel_id].usb = usb_volume
            if OutputVolumeConf[channel_id].output_device == 2:
                OutputVolumeConf[channel_id].volume = usb_volume
    else:
        logging.warning("invalid channel_id: {}".format(channel_id))


# 修改单点通话的音量
def change_user_output_volume(volume):
    global OutputVolumeConf
    OutputVolumeConf["phone"].usb = volume
    OutputVolumeConf["phone"].volume = volume


# 修改输出设备
def change_output_device(channel_id, device):
    global OutputVolumeConf
    if channel_id in OutputVolumeConf:
        OutputVolumeConf[channel_id].output_device = device
        OutputVolumeConf[channel_id].volume = OutputVolumeConf[channel_id].pc \
            if device == 1 else OutputVolumeConf[channel_id].usb
    else:
        logging.warning("invalid channel_id: {}".format(channel_id))


def get_channel_volume_conf(channel_id):
    global OutputVolumeConf
    if channel_id in OutputVolumeConf:
        return OutputVolumeConf[channel_id]
    else:
        logging.warning("invalid channel_id: {}".format(channel_id))


# 语音输入与输出
def init_devices():
    device_list = conf.get_device_conf()
    devices = {
        "inputs": [],
        "phone_input": [],
        "pc_outputs": [],
        "usb_outputs": [],
        "phone_output": []
    }

    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    for i in range(0, num_devices):
        max_input_channels = p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')
        max_output_channels = p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')
        name = p.get_device_info_by_host_api_device_index(0, i).get('name')
        if not name.endswith(")"):
            name += ")"
        if max_input_channels > 0:
            print("input device id ", i, "-", name)
            if name in device_list['phone_input']:
                devices["phone_input"].append(i)
            elif name in device_list['headset_input']:
                devices["inputs"].append(i)
        if max_output_channels > 0:
            print("output device id ", i, "-", name)
            if name in device_list['phone_output']:
                devices["phone_output"].append(i)
            elif name in device_list['headset_output']:
                devices["usb_outputs"].append(i)
            elif name in device_list['default_output']:
                devices["pc_outputs"].append(i)
    return devices


def change_volume(volume, data):
    volumeFactor = volume / 100
    multiplier = pow(2, (sqrt(sqrt(sqrt(volumeFactor))) * 192 - 192) / 6)

    # Doing Something To Data Here To Increase Volume Of It
    numpy_data = np.fromstring(data, dtype=np.int16)
    # double the volume using the factor computed above
    np.multiply(numpy_data, multiplier,
                out=numpy_data, casting="unsafe")

    return numpy_data.tostring()


class ChatClient:
    def __init__(self, ip, port):
        self.col_user = col_user
        self.col_channel = col_channel

        # self.speaking_channels = set()
        # self.speaking_users = set()
        self.user = {
            "id": "",  # id
            "name": "",
            "ip": ip,
            "port": port,  # udp端口
        }
        self.users_info = {}  # 客户端的信息

        # users
        users = self.col_user.find()
        for u in users:
            if self.user["ip"] == u["ip"] and self.user["port"] == u["port"]:
                self.user["name"] = u["name"]
                self.user["id"] = str(u["_id"])
            else:
                self.users_info[str(u["_id"])] = {
                    "id": str(u["_id"]),
                    "name": u["name"],
                    "ip": u["ip"],
                    "port": int(u["port"]),
                    "page": int(u["page"])
                }
        # channels
        self.ChannelsInfo = {}  # channel的信息
        self.availableChannels = []
        global OutputVolumeConf  # 用于通道音量控制
        channel_ret = self.col_channel.find()
        for c in channel_ret:
            channel_id = str(c["_id"])
            self.ChannelsInfo[channel_id] = {"port": c["port"], "ip": c["ip"], "status": c["status"]}
            if c["status"] == 1:
                self.availableChannels.append(channel_id)
                OutputVolumeConf[channel_id] = OutputConf()

        # 消息发送结束标识
        self.voice_send_flag_for_channel = False
        self.voice_send_flag_for_uer = False
        self.voice_record_flag_for_channel = False
        self.voice_record_flag_for_user = False
        self.exit_flag = False

        # 发消息
        self.cur_connect_user = None  # 当前选择通话的用户
        self.cur_speaking_channel = None  # 当前占用的通道
        self.cur_listening_channels = []  # 当前监听的通道

        # udp
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 输入输出设备信息初始化（用于记录和播放声音）
        self.devices = init_devices()
        logging.info("devices:{}".format(self.devices))

        # 输出设备音量初始化为100
        init_output_device_volume()

        self.record_frames_channel = Queue()
        self.record_frames_user = Queue()
        self.play_frames_for_channel_pc = Queue()
        self.play_frames_for_channel_usb = Queue()
        self.play_frames_for_user = Queue()
        # 记录输入设备状态
        self.input_device_flags = {}
        for input_id in self.devices["inputs"]:
            self.input_device_flags[input_id] = False

        # audio conf
        self.p = pyaudio.PyAudio()
        self.chunk_size = 350  # 512
        self.audio_format = pyaudio.paInt16
        self.audio_channels = 1
        self.rate = 4000

        # 通道通话
        self.playing_streams_for_channel = {"pc": [], "usb": []}

        # 脚踏板控制器
        self.ser = serial.Serial(None, 9600, rtscts=True, dsrdtr=True)
        self.ser.setPort(conf.get_serial())
        self.ser.dtr = True
        # 脚踏板启动
        self.ser.open()

    def start(self):
        # 扬声器播放
        for pc_op_id in self.devices["pc_outputs"]:
            self.playing_streams_for_channel["pc"].append(
                self.p.open(format=self.audio_format, channels=self.audio_channels, rate=self.rate,
                            output=True, frames_per_buffer=self.chunk_size, output_device_index=pc_op_id))
        # 耳机播放
        for usb_op_id in self.devices["usb_outputs"]:
            self.playing_streams_for_channel["usb"].append(
                self.p.open(format=self.audio_format, channels=self.audio_channels, rate=self.rate,
                            output=True, frames_per_buffer=self.chunk_size, output_device_index=usb_op_id))
        # TODO debug 用户电话
        if len(self.devices['phone_output']) > 0:
            self.playing_stream_for_user = self.p.open(format=self.audio_format, channels=self.audio_channels,
                                                       rate=self.rate, output=True, frames_per_buffer=self.chunk_size,
                                                       output_device_index=self.devices["phone_output"][0])

        self.s.bind((self.user["ip"], self.user["port"]))
        # 接收udp消息
        threading.Thread(target=self.receive_server_data).start()
        # 处理udp语音消息
        threading.Thread(target=self.voice_play_by_pc_for_channel).start()
        threading.Thread(target=self.voice_play_by_usb_for_channel).start()
        threading.Thread(target=self.voice_play_for_user).start()

    # 监听数据
    def receive_server_data(self):
        global speaking_users, speaking_channels, OutputVolumeConf

        while not self.exit_flag:
            try:
                data, _server = self.s.recvfrom(2048)
                msg = UdpMsg(msg=data)
                msg_body = json.loads(msg.getBody())

                # 单点通话消息
                if msg.msgType == 101:
                    if msg_body["from"] == self.cur_connect_user:
                        logging.info("客户端播放，name: {}".format(msg_body["from"]))
                        # 调节音量
                        volume = OutputVolumeConf['phone'].volume
                        voice_data = change_volume(volume, msg.getVoiceData())
                        self.play_frames_for_user.put(voice_data)
                    else:
                        speaking_users.add(msg_body["from"])
                        self.user_receive_channel = msg_body["channel_id"]
                        self.user_receive_call_id = msg_body["call_id"]
                # 通道消息
                elif msg.msgType == 100:
                    if msg_body["channel_id"] in self.cur_listening_channels:
                        # 调节音量
                        volume_value = OutputVolumeConf[msg_body["channel_id"]].volume
                        voice_data = change_volume(int(volume_value), msg.getVoiceData())
                        if OutputVolumeConf[msg_body["channel_id"]].output_device == 1:
                            # 默认扬声器播放
                            self.play_frames_for_channel_pc.put(voice_data)
                        else:
                            # 耳机播放
                            self.play_frames_for_channel_usb.put(voice_data)
                    else:
                        # 提示有新消息
                        speaking_channels.add(msg_body["channel_id"])

            except Exception as e:
                logging.error("receive_server_data err {}".format(e))

        logging.info("stop receive_server_data.")

    def get_channel_for_user(self):
        channel_id = random.choice(list(self.availableChannels))
        return channel_id

    # 请求占用channel
    def choose_channel(self, channel_id):
        logging.info("choose_channel {} {}".format(channel_id, self.user))
        global CurChannel
        CurChannel = channel_id
        self.cur_speaking_channel = channel_id
        self.voice_record_flag_for_channel = True
        # 启动所有麦克风设备
        for input_device in self.devices["inputs"]:
            logging.info("start device:{}".format(input_device))
            threading.Thread(target=self.record_voice_data_for_channel, args=(input_device,)).start()
        return True

    # 取消占用channel
    def cancel_channel(self, channel_id):
        logging.info("cancel_channel {}".format(channel_id))
        global CurChannel
        CurChannel = None
        self.cur_speaking_channel = None
        self.stop_send_to_channel()
        # 所有输入设备停止工作
        self.voice_record_flag_for_channel = False
        return True

    # 开始收取输入设备为device_id的声音数据
    def start_record_voice_data_for_channel(self, device_id):
        logging.info("start_record_voice_data")
        self.input_device_flags[device_id] = True

    # 停止收取输入设备为device_id的声音数据
    def stop_record_voice_data_for_channel(self, device_id):
        logging.info("stop_record_voice_data")
        self.input_device_flags[device_id] = False

    # 收取声音数据
    def record_voice_data_for_channel(self, device_id):
        recording_stream = self.p.open(format=self.audio_format, channels=self.audio_channels, rate=self.rate,
                                       input=True, frames_per_buffer=self.chunk_size, input_device_index=device_id)
        while not self.exit_flag and self.voice_record_flag_for_channel:
            if self.input_device_flags[device_id]:
                data = recording_stream.read(self.chunk_size)
                self.record_frames_channel.put(data)
                if self.record_frames_channel.qsize() > 100:
                    # 防止按下按钮开始监听了但是发送端出现问题，不能发送消息，造成内存溢出
                    with self.record_frames_channel.mutex:
                        self.record_frames_channel.queue.clear()

        logging.info("stop send_voice_data.")
        return

    # 将声音数据发送到通道上 100
    def start_send_to_channel(self):
        logging.info("start_send_to_channel {}".format(self.cur_speaking_channel))

        self.voice_send_flag_for_channel = True
        threading.Thread(target=self.send_voice_data_for_channel, args=(self.cur_speaking_channel,)).start()

    # 停止向当前的通道发送数据
    def stop_send_to_channel(self):
        logging.info("stop_send_to_channel")
        self.voice_send_flag_for_channel = False

    def send_voice_data_for_channel(self, channel_id):
        logging.info("start send voice data to channel {}".format(channel_id))
        num = 0
        while not self.exit_flag and self.voice_send_flag_for_channel:
            if not self.record_frames_channel.empty() > 0:
                try:
                    body = {"from": self.user["id"], "channel_id": channel_id}
                    msg = UdpMsg(msgType=100, num=num, body=json.dumps(body),
                                 voiceData=self.record_frames_channel.get())
                    self.s.sendto(msg.getMsg(),
                                  (self.ChannelsInfo[channel_id]["ip"], self.ChannelsInfo[channel_id]["port"]))
                    num += 1
                    # 最大标号100000
                    if num == 100000:
                        num = 0
                except Exception as e:
                    logging.error("send_voice_data_for_channel err: {}".format(e))
        logging.info("stop send voice data to channel {}.".format(channel_id))

    # 播放声音
    def voice_play_by_usb_for_channel(self):
        while not self.exit_flag:
            while self.play_frames_for_channel_usb.qsize() > 4:
                while not self.play_frames_for_channel_usb.empty():
                    pf = self.play_frames_for_channel_usb.get()
                    # usb耳机的播放器播放
                    for pls in self.playing_streams_for_channel["usb"]:
                        pls.write(pf)
                    # time.sleep(0.8 * 2 * self.chunk_size / self.rate)
        for pls in self.playing_streams_for_channel["usb"]:
            pls.close()

    def voice_play_by_pc_for_channel(self):
        while not self.exit_flag:
            while self.play_frames_for_channel_pc.qsize() > 4:
                while not self.play_frames_for_channel_pc.empty():
                    pf = self.play_frames_for_channel_pc.get()
                    # 系统默认的播放器播放
                    for pls in self.playing_streams_for_channel["pc"]:
                        pls.write(pf)

        for pls in self.playing_streams_for_channel["pc"]:
            pls.close()

    def generate_user_call_id(self):
        return "{}{}".format(self.user['ip'].replace(".", ""), int(time.time()))

    # 将声音数据发送到客户端上 101
    def start_send_to_user(self, uid, receive=False):
        self.cur_connect_user = uid
        self.voice_send_flag_for_uer = True
        self.voice_record_flag_for_user = True

        if receive:
            channel_id = self.user_receive_channel
            call_id = self.user_receive_call_id
        else:
            channel_id = self.get_channel_for_user()
            call_id = self.generate_user_call_id()
        threading.Thread(target=self.record_voice_data_for_user).start()
        threading.Thread(target=self.send_voice_data_for_user, args=(uid, channel_id, call_id)).start()
        logging.info("start send_to_user {}".format(self.cur_connect_user))

    # 停止声音数据发送到客户端上 101
    def stop_send_to_user(self):
        logging.info("stop_send_to_user {}".format(self.cur_connect_user))
        self.cur_connect_user = None
        self.voice_send_flag_for_uer = False
        self.voice_record_flag_for_user = False

    def record_voice_data_for_user(self):
        recording_stream = self.p.open(format=self.audio_format, channels=self.audio_channels, rate=self.rate,
                                       input=True, frames_per_buffer=self.chunk_size,
                                       input_device_index=self.devices["phone_input"][0])
        while not self.exit_flag and self.voice_record_flag_for_user:
            data = recording_stream.read(self.chunk_size, exception_on_overflow=False)
            self.record_frames_user.put(data)
            if self.record_frames_user.qsize() > 100:
                # 防止按下按钮开始监听了但是发送端出现问题，不能发送消息，造成内存溢出
                with self.record_frames_user.mutex:
                    self.record_frames_user.queue.clear()

        recording_stream.close()
        logging.info("stop send_voice_data.")
        return

    # 发送给用户
    def send_voice_data_for_user(self, user_id, channel_id, call_id):
        logging.info("start send voice data to user {}.".format(user_id))
        num = 0
        while not self.exit_flag and self.voice_send_flag_for_uer:
            if not self.record_frames_user.empty():
                try:
                    body = {"from": self.user["id"], "to": user_id, "call_id": call_id, "channel_id": channel_id}
                    msg = UdpMsg(msgType=101, num=num, body=json.dumps(body),
                                 voiceData=self.record_frames_user.get())
                    self.s.sendto(msg.getMsg(),
                                  (self.ChannelsInfo[channel_id]["ip"], self.ChannelsInfo[channel_id]["port"]))
                    num += 1
                    # 最大标号100000
                    if num == 100000:
                        num = 0
                except Exception as e:
                    logging.error("send_voice_data_for_user err: {}".format(e))

        logging.info("stop send voice data to user {}.".format(user_id))

    def voice_play_for_user(self):
        while not self.exit_flag:
            while self.play_frames_for_user.qsize() > 4:
                while not self.play_frames_for_user.empty():
                    pf = self.play_frames_for_user.get()
                    self.playing_stream_for_user.write(pf)
        self.playing_stream_for_user.close()
        logging.info("stop voice_play_for_user.")

    # 开始监听某个channel
    def add_listening_channel(self, channel_id):
        logging.info("addListening_channel {}".format(channel_id))
        self.cur_listening_channels.append(channel_id)

        return

    def del_listening_channel(self, channel_id):
        logging.info("delListening_channel {}".format(channel_id))
        self.cur_listening_channels.remove(channel_id)

        return

    def exit(self):
        self.exit_flag = True
        self.s.close()
