from my_thread import MyThread
import socket
import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    base_port = 9000
    # init channels
    ids = [1, 2, 3, 4, 5, 6, 7, 8]
    for i in range(len(ids)):
        MyThread(ids[i], socket.gethostbyname(socket.gethostname()), base_port + i).start()
