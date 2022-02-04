import socket
import threading
import random
import time
import my_udp
import logging
import json

SERVER_IP = "192.168.123.78"

PORTS = [9000, 9001, 9002, 9003, 9004, 9005, 9006, 9007]
#
# local_port = 8001
# listening_clients = [("192.168.123.78", 8002)]  # set
# listening_channels = [1, 2]  # set


#
#
# local_port = 8002
# listening_clients = [("192.168.123.78", 8001)]  # set
# listening_channels = [6, 7]  # set
#

local_port = 8003
listening_clients = [("192.168.123.78", 8001), ("192.168.123.78", 8002)] # set
listening_channels = [8]  # set


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
    return PORTS[i]


def getServerIP():
    return SERVER_IP


# 获取客户端信息
def getClients():
    # 从mongo获取
    return {
        ("192.168.123.78", 8001): {
            "name": "张1",
            "ip": "192.168.123.1"
        },
        ("192.168.123.78", 8002): {
            "name": "张2",
            "ip": "192.168.123.1"
        },
        ("192.168.123.78", 8003): {
            "name": "张3",
            "ip": "192.168.123.1"
        }
    }


class ChatClient:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(("192.168.123.78", local_port))

        # chunk_size = 1024  # 512
        # audio_format = pyaudio.paInt16
        # channels = 1
        # rate = 20000

        # self.p = pyaudio.PyAudio()
        # # 打开一个数据流对象，解码而成的帧将直接通过它播放出来，我们就能听到声音啦
        # self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True,
        #                                   frames_per_buffer=chunk_size)
        # self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True,
        #                                     frames_per_buffer=chunk_size)

        # start threads
        threading.Thread(target=self.receive_server_data).start()
        self.send_data_to_server()

    def receive_server_data(self):
        clients = getClients()
        while True:
            # try:
            data, _server = self.s.recvfrom(1500)
            msg = my_udp.udpMsg(voiceDataLen=len("adas"), msg=data)
            msg_body = json.loads(msg.getBody())
            logging.info("receive form {},name: {}, channel:{}".format(msg_body["from"], msg_body["from"],
                                                                       msg_body["channel"]))
            # TODO 获取当前监听的的客户端,直接播放
            if msg_body["from"] in listening_clients:
                logging.info("【监听客户端】播放，name: {}".format(msg_body["from"]))
            #    self.playing_stream.write(data)
            # TODO 是当前监听的信道，直接播放
            if msg_body["channel"] in listening_channels:
                logging.info("【监听信道】 播放，name: {}, channel:{}".format(msg_body["from"], msg_body["channel"]))
            #    self.playing_stream.write(data)

            # TODO 变色, 显示说话状态

            #
        # except Exception as e:
        #     print("err {}".format(e))

    def send_data_to_server(self):
        while True:
            try:
                # data = self.recording_stream.read(1024, exception_on_overflow=False)
                self.s.sendto("adas".encode(), (getServerIP(), getServerPort()))
            except Exception as e:
                logging.error("send_data_to_server err: {}".format(e))
            time.sleep(5)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

client = ChatClient()
