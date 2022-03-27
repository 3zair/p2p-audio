import pymongo

"""
修改数据库名称、ip地址
然后执行此脚本初始化数据库
"""
if __name__ == '__main__':
    myclient = pymongo.MongoClient("mongodb://admin:admin123@121.36.136.254:27017/")
    db = myclient["audio"]
    col_user = db["user"]
    col_channel = db["channel"]
    #
    col_channel.drop()
    col_user.drop()

    col_channel.insert_many([{"_id": "1", "port": 9001, "ip": "192.168.31.21", "status": 1},
                             {"_id": "2", "port": 9002, "ip": "192.168.31.21", "status": 1},
                             {"_id": "3", "port": 9003, "ip": "192.168.31.21", "status": 1},
                             {"_id": "4", "port": 9004, "ip": "192.168.31.21", "status": 1},
                             {"_id": "5", "port": 9005, "ip": "192.168.31.21", "status": 1},
                             {"_id": "6", "port": 9006, "ip": "192.168.31.21", "status": 1},
                             {"_id": "7", "port": 9007, "ip": "192.168.31.21", "status": 1},
                             {"_id": "8", "port": 9008, "ip": "192.168.31.21", "status": 1},
                             {"_id": "9", "port": 9009, "ip": "192.168.31.21", "status": 1},
                             {"_id": "10", "port": 9010, "ip": "192.168.31.21", "status": 1},
                             {"_id": "11", "port": 9012, "ip": "192.168.31.21", "status": 1},
                             {"_id": "13", "port": 9013, "ip": "192.168.31.21", "status": 1},
                             {"_id": "14", "port": 9014, "ip": "192.168.31.21", "status": 1},
                             {"_id": "15", "port": 9015, "ip": "192.168.31.21", "status": 1},
                             {"_id": "16", "port": 9016, "ip": "192.168.31.21", "status": 1},
                             ])

    col_user.insert_one({"name": "张1", "ip": "192.168.31.54", "port": 8001})
    col_user.insert_one({"name": "张2", "ip": "192.168.31.101", "port": 8002})
    col_user.insert_one({"name": "张3", "ip": "192.168.31.143", "port": 8003})
    col_user.insert_one({"name": "张4", "ip": "192.168.31.26", "port": 8004})
    col_user.insert_one({"name": "张5", "ip": "192.168.31.236", "port": 8005})
