import threading
import socket


class ChatServer:
    # 建立IPv4,UDP的socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 绑定端口：
    s.bind(('192.168.110.189', 9999))
    # 不需要开启listen，直接接收所有的数据
    print('Bind UDP on 9999')
    while True:
        # 接收来自客户端的数据,使用recvfrom
        data, addr = s.recvfrom(1024)
        print('Received from %s:%s.' % addr)
        s.sendto(b'hello, %s!' % data, addr)


# class ChatServer:
#     def __init__(self):
#         self.ip = socket.gethostbyname(socket.gethostname())
#         while True:
#             try:
#                 self.port = 9808
#                 self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#                 self.s.bind((self.ip, self.port))
#                 break
#             except:
#                 print("Couldn't bind to that port")
#
#         self.connections = []
#         self.accept_connections()
#
#     def accept_connections(self):
#         # self.s.listen(100)
#
#         print('Running on IP: ' + self.ip)
#         print('Running on port: ' + str(self.port))
#
#         while True:
#             # c, addr = self.s.accept()
#             #
#             # self.connections.append(c)
#
#             threading.Thread(target=self.handle_client, args=(c, addr,)).start()
#
#     def broadcast(self, sock, data, addr):
#         for client in self.connections:
#             if client != self.s and client != sock:
#                 try:
#                     client.sendto(data, addr)
#                 except:
#                     pass
#
#     def handle_client(self, c, addr):
#         while 1:
#             try:
#                 data = c.recvfrom(1024)
#                 print(data)
#                 self.broadcast(c, data, addr)
#
#             except socket.error:
#                 c.close()


server = ChatServer()