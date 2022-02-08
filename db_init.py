import pymongo

"""
修改数据库名称、ip地址
然后执行此脚本初始化数据库
"""

myclient = pymongo.MongoClient("mongodb://admin:admin123@121.36.136.254:27017/")
db = myclient["audio"]
col_user = db["user"]
col_channel = db["channel"]

col_channel.insert_many([{"_id": "1", "port": 9001, "ip": "192.168.31.26"}])
# {"_id": "2", "port": 9002, "ip": "192.168.31.26"},
# {"_id": "3", "port": 9003, "ip": "192.168.31.26"},
# {"_id": "4", "port": 9004, "ip": "192.168.31.26"},
# {"_id": "5", "port": 9005, "ip": "192.168.31.26"},
# {"_id": "6", "port": 9006, "ip": "192.168.31.26"},
# {"_id": "7", "port": 9007, "ip": "192.168.31.26"},
# {"_id": "8", "port": 9008, "ip": "192.168.31.26"},

#
col_user.insert_one({"name": "张1", "ip": "192.168.31.54", "level": 0, "port": 8001, "listening_channels": ["1"]})
col_user.insert_one({"name": "张2", "ip": "192.168.31.26", "level": 1, "port": 8002, "listening_channels": []})
# col_user.insert_one({"name": "张3", "ip": "192.168.31.26", "level": 1, "port": 8003, "listening_channels": [4, 2]})
# col_user.insert_one({"name": "张4", "ip": "192.168.31.26", "level": 2, "port": 8004, "listening_channels": [5, 2]})
# col_user.insert_one({"name": "张5", "ip": "192.168.31.26", "level": 2, "port": 8005, "listening_channels": [7, 2]})
# col_user.insert_one({"name": "张6", "ip": "192.168.31.26", "level": 3, "port": 8006, "listening_channels": [8, 2]})
# col_user.insert_one({"name": "张7", "ip": "192.168.31.26", "level": 3, "port": 8007, "listening_channels": []})
