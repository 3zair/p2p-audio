import socket
import my_udp
import json

TEST_CLIENT_IP = socket.gethostbyname(socket.gethostname())


def getClients():
    return [(TEST_CLIENT_IP, 8001), (TEST_CLIENT_IP, 8002), (TEST_CLIENT_IP, 8003)]


class ChatServer:
    def __init__(self, id, ip, port):
        # 建立IPv4,UDP的socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 绑定端口：
        s.bind((ip, port))
        # 不需要开启listen，直接接收所有的数据
        print('Bind UDP on {}'.format(port))

        clients = getClients()
        while True:
            # 接收来自客户端的数据,使用recvfrom
            data, addr = s.recvfrom(1500)
            print('Received from {}'.format(addr))
            for c in clients:
                # broadcast
                if c == addr:
                    continue
                msg = my_udp.udpMsg(body=json.dumps({"from": addr, "channel": id}), voiceDataLen=len("adas"),
                                    voiceData=data)
                s.sendto(msg.getMsg(), c)
