import socket
import threading
import pyaudio


class ChatClient:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while 1:
            try:
                self.target_ip = '192.168.110.189'
                self.target_port = 9808

                self.s.connect((self.target_ip, self.target_port))

                break
            except:
                print("Couldn't connect to server")

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

        print("Connected to Server")

        # start threads
        receive_thread = threading.Thread(target=self.receive_server_data).start()
        self.send_data_to_server()

    def receive_server_data(self):
        while True:
            try:
                data = self.s.recv(1024)
                self.playing_stream.write(data)
            except:
                pass

    def send_data_to_server(self):
        while True:
            try:
                data = self.recording_stream.read(1024, exception_on_overflow=False)
                self.s.sendall(data)
            except:
                pass


client = ChatClient()