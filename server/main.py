import os
import logging
import threading
import yaml
import server

from mgo import Mgo

CONF_PATH = os.path.join(os.getcwd(), "conf.yml")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    with open(CONF_PATH, 'r', encoding="utf-8") as conf_f:
        c = yaml.load(conf_f.read(), yaml.FullLoader)
    storage_dir = c["storage"]['root']

    if not os.path.exists(storage_dir):
        os.mkdir(storage_dir)

    mgo = Mgo(c['mongo']["url"], c["mongo"]["db"])
    channels = mgo.get_channels()
    clients = mgo.get_clients()
    for channel_id in channels.keys():
        if channels[channel_id]["status"] == 1:
            channel_server = server.ChatServer(
                channel_id, channels[channel_id]["ip"], channels[channel_id]["port"], clients, storage_dir)
            threading.Thread(target=channel_server.start_channel, args=(mgo,)).start()
