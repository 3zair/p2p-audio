import socket
import my_udp
import json
import pymongo
import logging
import struct
import mgo
import threading

VOICE_THUNK_SIZE = 1024


class ChatServer:
    def __init__(self):
        base_port = 9000
        # init channels
        ids = [1, 2, 3, 4, 5, 6, 7, 8]
        self.channels = mgo.getChannels()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        for i in range(len(ids)):
            threading.Thread(target=self.serverStart,
                             args=(ids[i], socket.gethostbyname(socket.gethostname()), base_port + i)).start()

    def serverStart(self, id, ip, port):
        # 建立IPv4,UDP的socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 绑定端口：
        s.bind((ip, port))

        # 不需要开启listen，直接接收所有的数据
        print('Bind UDP on {}'.format(port))

        clients = mgo.getClients()
        while True:
            # 接收来自客户端的数据,使用recv from
            data, addr = s.recvfrom(4096)
            msg = my_udp.udpMsg(msg=data)
            if msg.msgType in [100, 101]:
                for uid in clients.keys():
                    # broadcast
                    if clients[uid]["ip"] == addr[0] and clients[uid]["port"] == addr[1]:
                        continue
                    s.sendto(msg.getMsg(), (clients[uid]["ip"], clients[uid]["port"]))
            # 200 占用通道请求
            if msg.msgType == 200:
                body = json.loads(msg.getBody())
                if body["channel_id"] in self.channels:
                    if "cur_user" not in self.channels[body["channel_id"]] or \
                            self.channels[body["channel_id"]]["cur_user"] is None:
                        # 占用成功
                        self.channels[body["channel_id"]]["cur_user"] = body["uid"]
                        ret_msg = my_udp.udpMsg(200, json.dumps({"ret": True}), voiceData="")
                        s.sendto(ret_msg.getMsg(), addr)
                    else:
                        # 当前channel已被占用，返回失败
                        ret_msg = my_udp.udpMsg(200, json.dumps(
                            {"ret": False, "cur_uid": self.channels[body["channel_id"]]["cur_user"]}),
                                                voiceData="")
                        s.sendto(ret_msg.getMsg(), addr)
                else:
                    logging.error("invalid channel_id: {}".format(body["channel_id"]))
            # 201 释放通道请求
            elif msg.msgType == 201:
                body = json.loads(msg.getBody())
                if body["channel_id"] in self.channels:
                    if "cur_user" in self.channels[body["channel_id"]] and \
                            self.channels[body["channel_id"]]["cur_user"] == body["uid"]:
                        # 释放成功
                        self.channels[body["channel_id"]]["cur_user"] = None
                        ret_msg = my_udp.udpMsg(200, json.dumps({"ret": True}), voiceData="")
                        s.sendto(ret_msg.getMsg(), addr)
                    else:
                        logging.warning(
                            "释放通道失败 用户ID或者通道ID错误: uid:{} channel_id:{}".format(body["uid"], body["channel_id"]))
                        # 当前用户已不再占用当前通道
                        ret_msg = my_udp.udpMsg(200, json.dumps({"ret": True}), voiceData="")
                        s.sendto(ret_msg.getMsg(), addr)
                else:
                    logging.error("invalid channel_id: {}".format(body["channel_id"]))


# start
ChatServer()
