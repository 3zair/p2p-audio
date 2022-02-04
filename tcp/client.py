import socket
import threading
import pyaudio
import logging
import conf
import json
import struct
import time
import multiprocessing


class ClientInfo:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip


def getClientInfoKey(ip, port):
    return "{}:{}".format(ip, port)


class ChatClient:
    ip = socket.gethostbyname(socket.gethostname())
    user = "user"
    clientInfos = dict()
    clientInfoUT = time.time()
    voice_process = None

    def __init__(self, name, server_ip, server_port):
        self.user = name if name == "" else "user" + self.ip
        self.tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect
        try:
            self.tcp_client.connect((server_ip, server_port))
            logging.info("connect to {}:{}".format(server_ip, server_port))
        except socket.error as msg:
            logging.info("connect to server error:{}".format(msg))
            return

        # 定义语音消息参数

        self.p = pyaudio.PyAudio()
        # 打开数据流对象，解码而成的帧将直接通过它播放出来，我们就能听到声音啦
        self.playing_stream = self.p.open(format=conf.audio_format, channels=conf.channels, rate=conf.rate, output=True,
                                          frames_per_buffer=conf.chunk_size)

        threading.Thread(target=self.receive).start()

        # 上报客户端信息
        body = json.dumps(
            {"name": self.user, "type": conf.CLIENT_ADD, "ip": self.ip, "t": time.time()})
        header = [conf.MSG_EXCHANGE, body.__len__()]
        self.tcp_client.sendall(struct.pack("!II", *header) + body.encode())

        threading.Thread(target=self.health).start()

    def receive(self):
        data_buffer = bytes()
        while True:
            data = self.tcp_client.recv(1024)
            if data:
                data_buffer += data
                if len(data_buffer) < conf.HEADER_SIZE:
                    continue

                head_pack = struct.unpack('!II', data[:conf.HEADER_SIZE])
                body_size = head_pack[1]

                # # 播放语音消息

                if len(data_buffer) < conf.HEADER_SIZE + body_size:
                    continue

                if head_pack[0] == conf.MSG_Voice:
                    # 语音消息
                    self.playing_stream.write(data[conf.HEADER_SIZE:conf.HEADER_SIZE + body_size])
                elif head_pack[0] == conf.MSG_EXCHANGE:
                    # 客户端信息更新
                    json_body_data = data_buffer[conf.HEADER_SIZE:conf.HEADER_SIZE + body_size]
                    self.msgExchangeHandle(json_body_data)
                else:
                    logging.error("invalid msg type:{}".format(head_pack[0]))

                data_buffer = data_buffer[conf.HEADER_SIZE + body_size:]

    def msgExchangeHandle(self, data):
        msg = json.loads(data)
        # 如果是过期消息就丢弃
        if msg["t"] < self.clientInfoUT:
            logging.warning("expired msg:{}".format(msg))
            return

        if msg["type"] == conf.CLIENT_ADD:
            self.clientInfos[msg["name"]] = ClientInfo(msg["name"], msg["ip"])
            self.clientInfoUT = msg["t"]
            logging.info("add clients,{}".format(msg["name"]))

        elif msg["type"] == conf.CLIENT_DEL:
            del self.clientInfos[msg["name"]]
            self.clientInfoUT = msg["t"]
            logging.info("del clients".format(msg["name"]))

        elif msg["type"] == conf.CLIENT_UPDATE_ALL:
            for info in msg["info"]:
                self.clientInfos[info["name"]] = ClientInfo(info["name"], info["ip"])
                logging.info(info)
            self.clientInfoUT = msg["t"]
        else:
            logging.error("invalid msg type. msg:{}".format(msg))

    def send_data_to_server(self, des):
        recording_stream = self.p.open(format=conf.audio_format, channels=conf.channels, rate=conf.rate,
                                       input=True, frames_per_buffer=conf.chunk_size)
        while True:
            try:
                data = recording_stream.read(conf.AUDIO_BYTE_SIZE, exception_on_overflow=False)
                msg = json.dumps({"from": self.user, "to": des})
                header = [conf.MSG_Voice, conf.AUDIO_BYTE_SIZE + msg.__len__()]
                self.tcp_client.sendall(struct.pack("!II", *header) + data + msg.encode())
            except:
                pass

    def health(self):
        while True:
            header = [conf.MSG_HEALTHY, 1]
            self.tcp_client.sendall(struct.pack("!II", *header) + "a".encode())
            time.sleep(1)

    def sendVoiceMsg(self, name):
        # 启动语音消息发送多线程
        self.voice_process = multiprocessing.Process(target=self.send_data_to_server, args=(name,))
        self.voice_process.start()

    def stopSendVoiceMsg(self):
        self.voice_process.terminate()


# todo 1. 检测服务端断开连接, 2. 整体更新
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
client = ChatClient("user2", "192.168.123.78", 9001)
