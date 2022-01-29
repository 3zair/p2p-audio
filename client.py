import socket
import threading
import pyaudio
import logging
import conf
import json
import struct
import random
import time


class ClientInfo:
    def __init__(self, name, ip, port):
        self.name = name
        self.ip = ip
        self.port = port


class ChatClient:
    ip = socket.gethostbyname(socket.gethostname())
    user = "user"
    # key: username, value: ClientInfo
    clientInfos = dict()
    clientInfoUT = time.time()

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

        threading.Thread(target=self.receive).start()

        # 上报客户端信息
        body = json.dumps(
            {"name": self.user, "type": conf.CLIENT_ADD, "ip": self.ip, "udp_port": 9000, "t": time.time()})
        header = [conf.MSG_EXCHANGE, body.__len__()]
        self.send(struct.pack("!II", *header) + body.encode())

        threading.Thread(target=self.health).start()

    def receive(self):
        data_buffer = bytes()

        while True:
            data = self.tcp_client.recv(1024)

            if data:
                if len(data_buffer) < conf.HEADER_SIZE:
                    continue

                head_pack = struct.unpack('!If', data[:conf.HEADER_SIZE])

                data_buffer += data
                body_size = head_pack[1]
                if len(data_buffer) < conf.HEADER_SIZE + body_size:
                    continue

                # 解析消息
                json_body_data = data_buffer[conf.HEADER_SIZE:conf.HEADER_SIZE + body_size]
                self.msgHandle(json_body_data)

                data_buffer = data_buffer[conf.HEADER_SIZE + body_size:]

    def msgHandle(self, data):
        msg = json.loads(data)
        # 如果是过期消息就丢弃
        if msg["t"] < self.clientInfoUT:
            logging.warning("expired msg:{}".format(msg))
            return

        if msg["type"] == conf.CLIENT_ADD:
            self.clientInfos[msg["ip"] + msg["udp_port"]] = ClientInfo(msg["name"], msg["ip"], msg["udp_port"])
            self.clientInfoUT = msg["t"]
            logging.info("add clients,{}".format(msg["name"]))
        elif msg["type"] == conf.CLIENT_DEL:
            del self.clientInfos[msg["ip"] + msg["udp_port"]]
            self.clientInfoUT = msg["t"]
            logging.info("del clients".format(msg["name"]))
        elif msg["type"] == conf.CLIENT_UPDATE_ALL:
            logging.info(msg)
        else:
            logging.error("invalid msg type. msg:{}".format(msg))

    def send(self, data):
        try:
            self.tcp_client.sendall(data)
        except socket.error as msg:
            return msg

    def health(self):
        while True:
            header = [conf.MSG_HEALTHY, 1]
            self.send(struct.pack("!II", *header) + "a".encode())
            time.sleep(1)


# todo 1. 检测服务端断开连接, 2. 整体更新
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
client = ChatClient("user2", "192.168.123.78", 9001)
