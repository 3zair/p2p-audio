import threading
import socket
import logging
import json
import conf
import struct
import time


class ChatServer:
    def __init__(self, ip, port):
        self.port = port
        self.ip = ip
        logging.info("server config: ip:{} port:{}".format(self.ip, self.port))
        while True:
            try:
                self.tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tcp_server.bind((self.ip, self.port))
                break
            except socket.error as msg:
                logging.info("Couldn't bind to that port {},err:{}".format(self.port, msg))
                time.sleep(1)

        self.clientInfos = dict()
        threading.Thread(target=self.updateClientInfo).start()
        self.accept_connections()

    def accept_connections(self):
        self.tcp_server.listen(100)
        logging.info('Running on {}:{}'.format(self.ip, self.port))
        while True:
            c, addr = self.tcp_server.accept()
            self.clientInfos[addr] = ({"conn": c})
            logging.info("new client: {}".format(addr))
            threading.Thread(target=self.receive, args=(c, addr,)).start()

    def broadcast(self, sock, data):
        for addr, info in self.clientInfos.items():
            logging.info("broadcast cur addr:{}".format(addr))
            if info["conn"] != self.tcp_server and info["conn"] != sock:
                try:
                    header = [conf.MSG_EXCHANGE, data.__len__()]
                    info["conn"].send(struct.pack("!II", *header) + data.encode())
                    logging.info("broadcast to:{}".format(addr))
                except socket.error as err:
                    logging.error("broadcast err:{}, to {}, data:{}".format(err, addr, data))

    def receive(self, c, addr):
        data_buffer = bytes()
        while True:
            data = c.recv(1024)
            if data:
                data_buffer += data
                if len(data_buffer) < conf.HEADER_SIZE:
                    continue

                head_pack = struct.unpack('!II', data_buffer[:conf.HEADER_SIZE])
                body_size = head_pack[1]

                if head_pack[0] == conf.MSG_HEALTHY:
                    self.clientInfos[addr]["ut"] = time.time()
                    # logging.info("addr:{} healthy".format(addr))
                elif head_pack[0] == conf.MSG_EXCHANGE:
                    if len(data_buffer) < conf.HEADER_SIZE + body_size:
                        continue
                    json_body_data = data_buffer[conf.HEADER_SIZE:conf.HEADER_SIZE + body_size]

                    self.msgHandle(c, addr, json_body_data)

                data_buffer = data_buffer[conf.HEADER_SIZE + body_size:]

    def msgHandle(self, c, addr, data):
        print(data)
        msg = json.loads(data)
        logging.info(msg)
        if msg["type"] == conf.CLIENT_ADD:
            self.clientInfos[addr]["name"] = msg["name"]
            self.clientInfos[addr]["ip"] = msg["ip"]
            self.clientInfos[addr]["udp_port"] = msg["udp_port"]
            self.clientInfos[addr]["t"] = time.time()

            self.broadcast(c, json.dumps(
                {"name": msg["name"], "ip": msg["ip"], "udp_port": msg["udp_port"], "t": self.clientInfos[addr]["t"],
                 "type": conf.CLIENT_ADD}))
        elif msg["type"] == conf.CLIENT_ADD:
            self.broadcast(c, json.dumps(
                {"name": msg["name"], "ip": msg["ip"], "udp_port": msg["udp_port"], "t": time.time(),
                 "type": conf.CLIENT_DEL}))
            del self.clientInfos[addr]
        else:
            logging.error("invalid msg type. msg:{}".format(msg))
            return

    def updateClientInfo(self):
        while True:
            for addr, info in self.clientInfos.items():
                print("{} {} {}".format(time.time(), self.clientInfos[addr]["ut"],
                                        time.time() - self.clientInfos[addr]["ut"]))
                if time.time() - self.clientInfos[addr]["ut"] > 2:
                    self.broadcast(info[addr]["conn"], json.dumps(
                        {"name": info[addr]["name"], "ip": info[addr]["ip"], "udp_port": info[addr]["udp_port"],
                         "t": time.time(), "type": conf.CLIENT_DEL}))
                    del self.clientInfos[addr]
                    continue

                infos = []
                for key in self.clientInfos.keys():
                    if key != addr:
                        infos.append({"name": self.clientInfos[key]["name"], "ip": self.clientInfos[key]["ip"],
                                      "udp_port": self.clientInfos[key]["udp_port"]})
                if len(infos) == 0:
                    continue
                json_data = json.dumps({"type": conf.CLIENT_UPDATE_ALL, "info": infos, "t": time.time()})

                try:
                    header = [conf.MSG_EXCHANGE, json_data.__len__()]
                    info["conn"].send(struct.pack("!II", *header) + json_data.encode())
                    logging.info("update to:{}".format(addr))
                except socket.error as err:
                    logging.error("broadcast err:{}, to {}, data:{}".format(err, addr, json_data))
            time.sleep(2)


# todo 1. 检测客户端端口断开连接 2. 超时消息处理
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
server = ChatServer(socket.gethostbyname(socket.gethostname()), port=9001)
# server = ChatServer("0.0.0.0", port=9001)
