import socket
import threading
import random
import time
import my_udp
import logging
import json
import pyaudio
import wave
import random

SERVER_IP = socket.gethostbyname(socket.gethostname())
TEST_CLIENT_IP = socket.gethostbyname(socket.gethostname())

PORTS = [9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007]
#
local_port = 8001
listening_clients = [['192.168.110.123', 8002]]  # set
listening_channels = [1, 2]  # set

# local_port = 8002
# listening_clients = [(TEST_CLIENT_IP, 8001)]  # set
# listening_channels = [6, 7]  # set


# 开始听某个客户端的消息
def addListening_client(name):
    global listening_clients
    listening_clients.append(name)
    return


def delListening_client(name):
    global listening_clients
    listening_clients.remove(name)
    return


# 开始监听某个channel
def addListening_channel(id):
    global listening_channels
    listening_channels.append(id)
    return


def delListening_channel(id):
    global listening_channels
    listening_channels.remove(id)
    return


def getServerPort():
    i = random.randint(0, len(PORTS) - 1)
    return 9000


def getServerIP():
    return SERVER_IP


# 获取客户端信息
def getClients():
    # 从mongo获取
    return {
        ("192.168.110.189", 8001): {
            "name": "张1",
            "ip": "192.168.110.189"
        },
        ("192.168.110.123", 8002): {
            "name": "张2",
            "ip": "192.168.110.123"
        }
    }


class ChatClient:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((TEST_CLIENT_IP, local_port))

        self.chunk_size = 1024  # 512
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100

        self.RECORD_SECONDS = 10
        self.WAVE_OUTPUT_FILENAME = "output"

        self.p = pyaudio.PyAudio()
        # 打开一个数据流对象，解码而成的帧将直接通过它播放出来，我们就能听到声音啦
        self.playing_stream = self.p.open(format=self.audio_format, channels=self.channels, rate=self.rate, output=True,
                                          frames_per_buffer=self.chunk_size)
        self.recording_stream = self.p.open(format=self.audio_format, channels=self.channels, rate=self.rate, input=True,
                                            frames_per_buffer=self.chunk_size)

        # start threads
        threading.Thread(target=self.receive_server_data).start()
        self.send_data_to_server()

    def receive_server_data(self):
        clients = getClients()
        frames1 = []
        c = 0
        while True:
            c += 1
            # try:
            data, _server = self.s.recvfrom(1100)
            msg = my_udp.udpMsg(voiceDataLen=1024, msg=data)
            msg_body = json.loads(msg.getBody())
            logging.info("receive form {},name: {}, channel:{}".format(msg_body["from"], msg_body["from"],
                                                                       msg_body["channel"]))
            msg_voice = msg.getVoiceData()
            # TODO 获取当前监听的的客户端,直接播放
            if msg_body["from"] in listening_clients:
                logging.info("【监听客户端】播放，name: {}".format(msg_body["from"]))
                self.playing_stream.write(msg_voice)
                frames1.append(msg_voice)

            if c == 300:
                wf = wave.open("input" + str(c * random.randint(1, 20)) + ".wav", 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.p.get_sample_size(self.audio_format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames1))
                wf.close()
                frames1 = []
                c = 0

            # TODO 是当前监听的信道，直接播放
            # if msg_body["channel"] in listening_channels:
            #     logging.info("【监听信道】 播放，name: {}, channel:{}".format(msg_body["from"], msg_body["channel"]))
            #     self.playing_stream.write(msg_voice)

            # TODO 变色, 显示说话状态

            #
        # except Exception as e:
        # print("err {}".format(e))

    def send_data_to_server(self):
        count = 0
        while True:
            frames = []
            try:
                # data = self.recording_stream.read(1024, exception_on_overflow=False)
                count += 1
                for i in range(0, int(self.rate / self.chunk_size * self.RECORD_SECONDS)):
                    data = self.recording_stream.read(1024, exception_on_overflow=False)
                    self.s.sendto(data, (getServerIP(), getServerPort()))
                    frames.append(data)

                wf = wave.open(self.WAVE_OUTPUT_FILENAME + str(count) + ".wav", 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.p.get_sample_size(self.audio_format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
                wf.close()

                # self.s.sendto(data, (getServerIP(), getServerPort()))
                # self.s.sendto("adas".encode(), (getServerIP(), getServerPort()))
            except Exception as e:
                logging.error("send_data_to_server err: {}".format(e))


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

client = ChatClient()
