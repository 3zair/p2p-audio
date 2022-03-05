import socket
import threading
import logging
import json
import random
import wave

import pyaudio
import time
import serial

from .my_udp import UdpMsg
from common.mgo import col_user, col_channel

from .volume_control_utils import MyAudioUtilities
from comtypes import CLSCTX_ALL
from pycaw.pycaw import IAudioEndpointVolume
from ctypes import POINTER, cast

# 控制音量
OutputDevices = {
    "pc": [],
    "usb": []
}


def output_device_init_for_volume_control():
    global OutputDevices
    # 打印所有音频设备
    device_list = MyAudioUtilities.GetAllDevices()
    i = 0
    for device in device_list:
        if device.FriendlyName.find("扬声器") >= 0:
            if device.FriendlyName.find("USB") >= 0:
                OutputDevices["usb"].append(device)
            else:
                OutputDevices["pc"].append(device)
        i += 1


# 通道的输出设备相关配置
# key: channel_id
# value:[device,pc_volume,usb_volume]
#       device: pc=>1, usb=>2
ChannelsOutputVolumeConf = {}
CurChannel = None

# 默认耳机播放音频
CurOutputModel = 2


def set_output_volume_value(device, value):
    try:
        tmp = device.id
        devices = MyAudioUtilities.GetDevice(tmp)

        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(value / 100.0, None)
    except Exception as e:
        logging.warning("set_output_volume_value err:{}".format(e))


def change_output_volume(channel_id, device, usb_volume=-1, pc_volume=-1):
    global ChannelsOutputVolumeConf, CurChannel,CurOutputModel
    if channel_id in ChannelsOutputVolumeConf:
        ChannelsOutputVolumeConf[channel_id][0] = device
        CurOutputModel = device
        logging.info(ChannelsOutputVolumeConf)
        if pc_volume > -1:
            ChannelsOutputVolumeConf[channel_id][1] = pc_volume

            for device in OutputDevices["pc"]:
                set_output_volume_value(device, pc_volume)
        if usb_volume > -1:
            ChannelsOutputVolumeConf[channel_id][2] = usb_volume

            for device in OutputDevices["usb"]:
                set_output_volume_value(device, usb_volume)
    else:
        logging.warning("invalid channel_id: {}".format(channel_id))


def get_channel_volume_conf():
    global ChannelsOutputVolumeConf
    logging.info(ChannelsOutputVolumeConf)
    return ChannelsOutputVolumeConf


# 语音输入与输出
def init_devices():
    devices = {
        "inputs": [],
        "pc_outputs": [],
        "usb_outputs": []
    }

    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    for i in range(0, num_devices):
        max_input_channels = p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')
        max_output_channels = p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')
        name = p.get_device_info_by_host_api_device_index(0, i).get('name')
        if max_input_channels > 0 and name.find("USB") >= 0:
            print("input device id ", i, "-", name)
            devices["inputs"].append(i)
        if max_output_channels > 0:
            if name.find("USB") >= 0:
                print("usb output device id ", i, "-", name)
                devices["usb_outputs"].append(i)
            else:
                print("pc output device id ", i, "-", name)
                devices["pc_outputs"].append(i)
    return devices


class ChatClient:
    def __init__(self, ip, port):
        self.col_user = col_user
        self.col_channel = col_channel

        self.user = {
            "id": "",  # id
            "name": "",
            "ip": ip,
            "port": port,  # udp端口
            "listening_channels": [],  # [channel_id]  所监听的通道
            "listening_clients": []  # [uid] 所监听的客户端
        }
        self.ClientsInfo = {}  # 客户端的信息

        # users
        users = self.col_user.find()
        for u in users:
            if self.user["ip"] == u["ip"] and self.user["port"] == u["port"]:
                self.user["name"] = u["name"]
                self.user["id"] = str(u["_id"])
            else:
                self.ClientsInfo[str(u["_id"])] = {
                    "name": u["name"],
                    "ip": u["ip"],
                    "port": u["port"],
                }
        # channels
        self.ChannelsInfo = {}  # channel的信息
        self.availableChannels = []
        global ChannelsOutputVolumeConf  # 用于通道音量控制
        channel_ret = self.col_channel.find()
        for c in channel_ret:
            channel_id = str(c["_id"])
            self.ChannelsInfo[channel_id] = {"port": c["port"], "ip": c["ip"], "status": c["status"]}
            if c["status"] == 1:
                self.availableChannels.append(channel_id)
                ChannelsOutputVolumeConf[channel_id] = [2, 50, 50]

        # 消息发送结束标识
        self.ChannelFlag = False
        self.UserFlag = False
        self.VoiceRecordFlag = False
        self.exit_flag = False

        # 发消息
        self.cur_client = None  # 当前选择通话的用户
        self.cur_channel = None  # 当前占用的通道

        # udp
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((self.user["ip"], self.user["port"]))

        # 输入输出设备信息初始化（用于记录和播放声音）
        self.devices = init_devices()
        logging.info("devices:{}".format(self.devices))
        # 输出设备初始化（用于调节音量）
        output_device_init_for_volume_control()

        self.record_frames = []
        self.play_frames = []
        # 记录输入设备状态
        self.input_device_flags = {}
        for input_id in self.devices["inputs"]:
            self.input_device_flags[input_id] = False

        # audio conf
        self.p = pyaudio.PyAudio()
        self.chunk_size = 512  # 512
        self.audio_format = pyaudio.paInt16
        self.audio_channels = 1
        self.rate = 16000
        # play_streams
        self.playing_streams = {"pc": [], "usb": []}
        for pc_op_id in self.devices["pc_outputs"]:
            self.playing_streams["pc"].append(
                self.p.open(format=self.audio_format, channels=self.audio_channels, rate=self.rate,
                            output=True, frames_per_buffer=self.chunk_size, output_device_index=pc_op_id))
        for pc_op_id in self.devices["usb_outputs"]:
            self.playing_streams["usb"].append(
                self.p.open(format=self.audio_format, channels=self.audio_channels, rate=self.rate,
                            output=True, frames_per_buffer=self.chunk_size, output_device_index=pc_op_id))

        # 接收udp消息
        threading.Thread(target=self.receive_server_data).start()
        # 处理udp语音消息
        threading.Thread(target=self.play).start()

        # 脚踏板控制器
        self.ser = serial.Serial(None, 9600, rtscts=True, dsrdtr=True)
        self.ser.setPort("COM3")
        self.ser.dtr = True
        self.ser.open()

    # 监听数据
    def receive_server_data(self):
        channel_buffer, client_buffer = {}, {}
        channel_orders, client_orders = [], []
        f = wave.open("receive.wav", "wb")
        f.setnchannels(self.audio_channels)
        f.setsampwidth(self.p.get_sample_size(self.audio_format))
        f.setframerate(self.rate)
        frames = []
        while not self.exit_flag:
            try:
                data, _server = self.s.recvfrom(2048)
                msg = UdpMsg(msg=data)
                msg_body = json.loads(msg.getBody())

                # TODO 获取当前监听的的客户端,放入播放队列
                # if msg.msgType == 101 and msg_body["from"] in User["listening_clients"]:
                #     logging.info("【监听客户端】播放，name: {}".format(msg_body["from"]))
                #
                #     client_orders.append(msg.msgNum)
                #     client_buffer[msg.msgNum] = msg.getVoiceData()
                #     if len(client_orders) == 20:
                #         client_orders.sort()
                #         for t in client_orders:
                #             self.play_frames.append(client_buffer[t])
                #     client_orders = []
                #     client_buffer = {}

                # TODO 是当前监听的信道，放入播放队列
                if msg.msgType == 100 and msg_body["channel_id"] in self.user["listening_channels"]:
                    # logging.info("【监听信道】 播放，name: {}, channel:{} num:{}".format(
                    #     msg_body["from"], msg_body["channel_id"], msg.msgNum))
                    logging.info("voice data len{} num{} data:{}".format(len(msg.voiceData), msg.msgNum, msg.voiceData))

                    channel_orders.append(msg.msgNum)
                    channel_buffer[msg.msgNum] = msg.getVoiceData()
                    frames.append(msg.voiceData)
                    if len(channel_orders) == 10:
                        channel_orders.sort()
                        play_frame_body = []
                        for t in channel_orders:
                            # 放入播放队列
                            play_frame_body.append(channel_buffer[t])
                        self.play_frames.append(play_frame_body)
                        channel_orders = []
                        channel_buffer = {}

            except Exception as e:
                logging.error("receive_server_data err {}".format(e))

        f.writeframes(b''.join(frames))
        f.close()
        logging.info("stop receive_server_data.")

    # 请求占用channel
    def choose_channel(self, channel_id):
        logging.info("choose_channel {} {}".format(channel_id, self.user))
        global CurChannel
        CurChannel = channel_id
        self.cur_channel = channel_id
        self.VoiceRecordFlag = True
        # 启动所有麦克风设备
        for input_device in self.devices["inputs"]:
            threading.Thread(target=self.record_voice_data, args=(input_device,)).start()
        return True

    # 取消占用channel
    def cancel_channel(self, channel_id):
        logging.info("cancel_channel {}".format(channel_id))
        global CurChannel
        CurChannel = None
        self.cur_channel = None
        self.stop_send_to_channel()
        # 所有输入设备停止工作
        self.VoiceRecordFlag = False
        return True

    # 开始收取输入设备为device_id的声音数据
    def start_record_voice_data(self, device_id):
        logging.info("start_record_voice_data")
        self.input_device_flags[device_id] = True

    # 停止收取输入设备为device_id的声音数据
    def stop_record_voice_data(self, device_id):
        logging.info("stop_record_voice_data")
        self.input_device_flags[device_id] = False

    # 收取声音数据
    def record_voice_data(self, device_id):
        if device_id < 0:
            recording_stream = self.p.open(format=self.audio_format, channels=self.audio_channels, rate=self.rate,
                                           input=True, frames_per_buffer=self.chunk_size)
        else:
            recording_stream = self.p.open(format=self.audio_format, channels=self.audio_channels, rate=self.rate,
                                           input=True, frames_per_buffer=self.chunk_size, input_device_index=device_id)

        while not self.exit_flag and self.VoiceRecordFlag:
            # 打开一个数据流对象，解码而成的帧将直接通过它播放出来，我们就能听到声音啦
            data = recording_stream.read(self.chunk_size, exception_on_overflow=False)
            if self.input_device_flags[device_id]:
                self.record_frames.append(data)
                if len(self.record_frames) > 100:
                    # 防止按下按钮开始监听了但是发送端出现问题，不能发送消息，造成内存溢出
                    self.record_frames = []

        recording_stream.close()
        logging.info("stop send_voice_data.")
        return

    # 将声音数据发送到通道上 100
    def start_send_to_channel(self):
        logging.info("start_send_to_channel {}".format(self.cur_channel))

        self.ChannelFlag = True
        threading.Thread(target=self.send_voice_data, args=("channel", self.cur_channel)).start()

    # 停止向当前的通道发送数据
    def stop_send_to_channel(self):
        logging.info("stop_send_to_channel")
        self.ChannelFlag = False

    # 将声音数据发送到客户端上 101
    def send_to_user(self, uid):
        self.UserFlag = True
        threading.Thread(target=self.send_voice_data, args=("user", uid)).start()

    # 停止声音数据发送到客户端上 101
    def stop_send_to_user(self):
        logging.info("stop_send_to_user")
        self.UserFlag = False

    def send_voice_data(self, type, to_id):
        logging.info("start_send_voice_data")
        # 发送到通道
        if type == "channel":
            num = 0
            while not self.exit_flag and self.ChannelFlag:
                if len(self.record_frames) > 0:
                    try:
                        body = {"from": self.user["id"], "channel_id": to_id}
                        msg = UdpMsg(msgType=100, num=num, body=json.dumps(body),
                                     voiceData=self.record_frames.pop())
                        self.s.sendto(msg.getMsg(),
                                      (self.ChannelsInfo[to_id]["ip"], self.ChannelsInfo[to_id]["port"]))
                        logging.info("send len{} num{} data:{}".format(len(msg.voiceData), num, msg.voiceData))
                        num += 1
                        # 最大标号100000
                        if num == 100000:
                            num = 0
                    except Exception as e:
                        logging.error("send_data_to_server err: {}".format(e))
        # 发送给用户
        elif type == "user":
            num = 0
            while not self.exit_flag and self.UserFlag:
                if len(self.record_frames) > 0:
                    try:
                        # TODO
                        body = {"from": self.user["id"]}
                        msg = UdpMsg(msgType=101, num=num, body=json.dumps(body),
                                     voiceData=self.record_frames.pop())
                        self.s.sendto(msg.getMsg(),
                                      (self.ClientsInfo[to_id]["ip"], self.ClientsInfo[to_id]["port"]))
                        num += 1
                        # 最大标号100000
                        if num == 100000:
                            num = 0
                    except Exception as e:
                        logging.error("send_data_to_user err: {}".format(e))
        logging.info("stop send_voice_data.")

    # 播放声音
    def play(self):
        global CurOutputModel
        f = wave.open("receive2.wav", "wb")
        f.setnchannels(self.audio_channels)
        f.setsampwidth(self.p.get_sample_size(self.audio_format))
        f.setframerate(self.rate)
        frames = []
        while not self.exit_flag:
            if len(self.play_frames) > 0:
                pfs = self.play_frames.pop()
                for pf in pfs:
                    if CurOutputModel:
                        # 系统默认的播放器播放
                        for pls in self.playing_streams["pc"]:
                            pls.write(pf)
                    else:
                        # usb耳机的播放器播放
                        for pls in self.playing_streams["usb"]:
                            pls.write(pf)
                    time.sleep(0.8 * self.chunk_size / self.rate)
        f.writeframes(b''.join(frames))
        f.close()
        for pls in self.playing_streams["pc"]:
            pls.close()
        for pls in self.playing_streams["usb"]:
            pls.close()
        logging.info("stop play.")

    def get_channel(self):
        channel_id = random.choice(list(self.availableChannels))
        return self.ChannelsInfo[channel_id]["ip"], self.ChannelsInfo[channel_id]["port"]

    # 设置使用的信道
    def set_cur_channel(self, channel_id):
        logging.info("")
        self.cur_channel = channel_id
        return

    # 开始听某个客户端的消息
    def add_listening_client(self, uid):
        self.user["listening_clients"].append(uid)
        return

    def del_listening_client(self, uid):
        self.user["listening_clients"].remove(uid)

        return

    # 开始监听某个channel
    def add_listening_channel(self, channel_id):
        logging.info("addListening_channel {}".format(channel_id))
        self.user["listening_channels"].append(channel_id)

        return

    def del_listening_channel(self, channel_id):
        logging.info("delListening_channel {}".format(channel_id))
        self.user["listening_channels"].remove(channel_id)

        return

    def exit(self):
        self.exit_flag = True
        self.s.close()
