import pymongo
import sys

class MongoConn(object):
    def __init__(self, MONGODB_CONFIG=None):

        if MONGODB_CONFIG:
            self.MONGODB_CONFIG = MONGODB_CONFIG
        else:
            try:
                from phaser1.apscheduler.fatal_v11.cfg import SysLogMongoDBConfig
                # from config import MongoConfig
                self.MONGODB_CONFIG = SysLogMongoDBConfig
            except:
                self.MONGODB_CONFIG = dict(host='192.168.2.17', port=17017, db_name='fluent', username="root", password="string123")
        # connect db
        try:

            # uri = "mongodb://{username}:{password}{host}/?authSource={db}&authMechanism=SCRAM-SHA-1".format(
            #
            # )

            self.conn = pymongo.MongoClient(self.MONGODB_CONFIG['host'], self.MONGODB_CONFIG['port'])
            self.db = self.conn[self.MONGODB_CONFIG['db_name']]  # connect db
            self.username=self.MONGODB_CONFIG['username']
            self.password=self.MONGODB_CONFIG['password']
            if self.username and self.password:
                self.connected = self.db.authenticate(self.username, self.password)
            else:
                self.connected = True
        except Exception as e:
            print(e)
            sys.exit(1)

    def show_data(self, table='nginx_access_log'):
        my_conn = MongoConn()
        res = my_conn.db[table].find(projection={"_id":False})
        for x in res:
            print(x)

    def insert_data(self, table, data):
        from datetime import datetime
        syslog_stat = {"pre_data_len": len(data),
                       "opt_table": table,
                       "stat": "NoneExcept",
                       "runtime": str(datetime.now())}
        try:
            self.db[table].insert(data)
        except:
            pass
        finally:
            self.db["actionlog"].insert(syslog_stat)

    def insert_data_uniq(self, table, data, key="audit_logid"):
        # import numpy as np
        try:
            mongo_saved_data = [data[key] for data in self.db[table].find({})]
        except:
            mongo_saved_data = []
        res_data = [item for item in data if item[key] not in mongo_saved_data]
        ## 无重插入
        from datetime import datetime
        syslog_stat = {"pre_data_len": len(data), "opt_table": table, "stat": "Insert【" + str(len(res_data)) + "】条数据", "runtime": str(datetime.now())}
        try:
            self.db[table].insert(res_data)
        except:
            pass
        finally:
            self.db["actionlog"].insert(syslog_stat)

    def show_actions_logs(self):
        # return self.db["actionlog"].find()
        for x in self.db["actionlog"].find():
            print(x)

    def remove(self, table):
        self.db[table].remove()

    def show_by_condition(self, table, condition={}):
        # 根据条件进行查询，返回所有记录
        res = self.db[table].find(condition)
        for x in res:
            print(x)

    def show_actions(self):
        for x in self.db["actionlog"].find():
            print(x)

if __name__ == '__main__':
    # MongoConn().show_data(table='waf_alert_log')
    MongoConn().insert_data("test", [{"index": i} for i in range(200)])
    MongoConn().show_data(table='test')