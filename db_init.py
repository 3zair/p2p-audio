import pymongo

myclient = pymongo.MongoClient("mongodb://admin:admin123@121.36.136.254:27017/")
db = myclient["audio"]
col_user = db["user"]
col_channel = db["channel"]

# col_user.insert_one({"name": "张1", "ip": "192.168.123.78", "level": 0, "port": 8001})
# col_channel.insert_many([{"_id": "1", "port": 9001},
#                          {"_id": "2", "port": 9002},
#                          {"_id": "3", "port": 9003},
#                          {"_id": "4", "port": 9004},
#                          {"_id": "5", "port": 9005},
#                          {"_id": "6", "port": 9006},
#                          {"_id": "7", "port": 9007},
#                          {"_id": "8", "port": 9008},
#                          ])
col_user.insert_one({"name": "张1", "ip": "192.168.123.78", "level": 0, "port": 8001})
col_user.insert_one({"name": "张2", "ip": "192.168.123.78", "level": 1, "port": 8002})
col_user.insert_one({"name": "张3", "ip": "192.168.123.78", "level": 1, "port": 8003})
col_user.insert_one({"name": "张4", "ip": "192.168.123.78", "level": 2, "port": 8004})
col_user.insert_one({"name": "张5", "ip": "192.168.123.78", "level": 2, "port": 8005})
col_user.insert_one({"name": "张6", "ip": "192.168.123.78", "level": 3, "port": 8006})
col_user.insert_one({"name": "张7", "ip": "192.168.123.78", "level": 3, "port": 8007})
