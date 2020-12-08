#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
        Homepage: https://github.com/ucloud/ucloud-sdk-python3
        Examples: https://github.com/ucloud/ucloud-sdk-python3/tree/master/examples
        Documentation: https://ucloud.github.io/ucloud-sdk-python3/
"""

import time
import argparse
import wget
from ucloud.core import exc
from ucloud.client import Client


PUBLIC_KEY = "xxx"
PRIVATE_KEY = "xxx"


class DbInstance:
    def __init__(self):
        self.client = Client({
            "region": "us-ca",
            "project_id": "org-27257",
            "public_key": PUBLIC_KEY,
            "private_key": PRIVATE_KEY,
            "base_url": "https://api.ucloud.cn",
        })

    def getAllDbs(self):
        try:
            resp = self.client.udb().describe_udb_instance({
                "Zone": "us-ca-01",
                "ClassType": "SQL",
                "Offset": 0,
                "Limit": 100
            })
        except exc.UCloudException as e:
            print(e)
        else:
            return resp

    def getBinlogList(self, db_id, start_time, end_time):
        try:
            resp = self.client.udb().describe_udb_instance_binlog({
               "Zone": "us-ca-01",   # 洛杉矶可用A
               "DBId": db_id,
               "BeginTime": start_time,
               "EndTime": end_time
            })
        except exc.UcloudException as e:
            print(e)
        else:
            return resp       # {'DataSet': [{'BeginTime': 1604735964, 'EndTime': 1604737396, 'Name': 'mysql-bin.001070', 'Size': 1073742193}]}
                              # {'DataSet': [{'BeginTime': 1604735964, 'EndTime': 1604737396, 'Name': 'mysql-bin.001070', 'Size': 1073742193}, {'BeginTime': 1604737396, 'EndTime': 1604739046, 'Name': 'mysql-bin.001071', 'Size': 1073741886}, {'BeginTime': 1604739046, 'EndTime': 1604740713, 'Name': 'mysql-bin.001072', 'Size': 1073742901}]}

    def backupBinlog(self, db_id, binlog_file, backup_filename):
        try:
            resp = self.client.udb().backup_udb_instance_binlog({
                "Zone": "us-ca-01",
                "DBId": db_id,
                "BackupFile": binlog_file,
                "BackupName": backup_filename
            })
        except exc.UcloudException as e:
            print(e)
        else:
            return resp
        
    def getBackupList(self, offset=0, limit=10):
        try:
            resp = self.client.udb().describe_udb_log_package({
                "Zone": "us-ca-01",
                "Offset": offset,
                "Limit": limit
            })
        except exc.UcloudException as e:
            print(e)
        else:
            return resp

    def getBackupUrl(self, db_id, file_id):
        try:
            resp = self.client.udb().describe_udb_binlog_backup_url({
                "Zone": "us-ca-01",
                "DBId": db_id,
                "BackupId": int(file_id)
            })
        except exc.UcloudException as e:
            print(e)
        else:
            return resp


def format_time(string_time):
    # string_time格式为 %Y-%m-%d %H:%M ，精度到分钟
    timeArray = time.strptime(string_time, "%Y-%m-%d %H:%M") 
    return int(time.mktime(timeArray))


if __name__ == "__main__":
        db = DbInstance()
        databases = []
        for i in db.getAllDbs()['DataSet']:
            if len(i['DataSet']) != 0 :
                for j in i['DataSet']:
                    databases.append(j)
                    print("新增j:", j)
            else:
                databases.append(i)
                print("新增i:", i)


        dbs = db.getAllDbs()
        #print("dbs长度为:%d" % len(dbs['DataSet']))
        #print(dbs)
       


        #print("Ucloud Response....................")
        print(databases)
        print("databases长度为%d" % len(databases))



        #parser = argparse.ArgumentParser()
        #parser.add_argument("--starttime", "-s", help="开始时间", required=True)
        #parser.add_argument("--endtime", "-e", help="开始时间", required=True)

        #args = parser.parse_args()
        #start_time = format_time(args.starttime)
        #end_time = format_time(args.endtime)
        #log_suffix = args.starttime.split()[0].replace("-", "")


        #db = DbInstance()
        #slave_db_id = "udb-t3vlhn4e"
        #backup_file_name = "dylan-binlog-%s" % log_suffix
        #
        ## 只获取时间匹配的第一个的binlog文件来备份
        #binlog_file_info = db.getBinlogList(slave_db_id, start_time, end_time)["DataSet"][0]
        #
        ## 备份自已定义的binlog备份文件
        #binlog_filename = binlog_file_info["Name"]
        #db.backupBinlog(slave_db_id, binlog_filename, backup_file_name)

        ## 打包生成备份文件需要一段时间，这里阻塞30s
        #time.sleep(60)

        ## 获取backupfile的列表，找到匹配backup_file_name的备份文件id
        #backup_lists = db.getBackupList()["DataSet"]
        #for backup in backup_lists:
        #    if backup["BackupName"] == backup_file_name:
        #        file_id = backup["BackupId"]
        #        break
        #    else:
        #        continue
        #url = db.getBackupUrl(slave_db_id, file_id)
        #inner_url = url["InnerBackupPath"]
        #backup_url = url["BackupPath"]
        #print("Binlog备份文件内网下载链接: \n%s\n外网下载链接：\n %s" %(inner_url,backup_url))
        #print("开始下载文件...")
        #wget.download(backup_url)