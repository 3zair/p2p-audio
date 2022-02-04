import threading
from server import ChatServer


class MyThread(threading.Thread):
    def __init__(self, id, ip, port):
        threading.Thread.__init__(self)
        self.id = id
        self.ip = ip
        self.port = port

    def run(self):
        ChatServer(self.id, self.ip, self.port)
