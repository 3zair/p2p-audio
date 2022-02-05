import socket
import threading
import pyaudio
#
# s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# # 不需要建立连接：
# for data in [b'Michael', b'ALice', b'FF']:
#     # 发送数据到客户端：
#     s.sendto(data, ('127.0.0.1', 9999))
#     # 接收来自客户端的数据：
#     print(s.recvfrom(1024)[0].decode('utf-8'))
# s.close()


class ChatClient:
    user = ""
    clientInfos = dict()

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.s.bind(('192.168.110.189', 9999))

        chunk_size = 1024  # 512
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        self.p = pyaudio.PyAudio()
        # 打开一个数据流对象，解码而成的帧将直接通过它播放出来，我们就能听到声音啦
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=chunk_size)


        # start threads
        receive_thread = threading.Thread(target=self.receive_server_data).start()
        self.send_data_to_server()

    def receive_server_data(self):
        while True:
            try:
                data, address = self.s.recvfrom(1024)
                self.playing_stream.write(data)
            except:
                pass

    def send_data_to_server(self):
        while True:
            try:
                data = self.recording_stream.read(1024, exception_on_overflow=False)
                self.s.sendto(data, ('192.168.110.123', 9092))
            except:
                pass


client = ChatClient()