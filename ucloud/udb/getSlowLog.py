# coding:utf-8
import os
import time
import datetime
import shutil
import tarfile
from ucloud.core import exc


def gettimestamp(day):
    """
    因为时差15小时，所以生成slowlog日志时间选择增加15小时的，
    如想获取2019.1.1 00：00：00 到 2019.1.1 23：59：59的慢日志记录
    则时间选择为2019.1.1 15：00：00 到 2019.1.2 14：59：59
    """

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=day)
    yesterday_start_time = int(time.mktime(time.strptime(str(yesterday), '%Y-%m-%d'))) + 15 * 3600
    yesterday_end_time = int(time.mktime(time.strptime(str(today), '%Y-%m-%d'))) + 15 * 3600
    return yesterday_start_time, yesterday_end_time


def createslowlog(client, db_id, start_time, finish_time, log_name):
    """
    创建slowlog日志包
    :param client
    :param db_id:
    :param start_time:
    :param finish_time:
    :param log_name:
    :return:
    """
    try:
        resp = client.udb().backup_udb_instance_slow_log({
            "DBId": db_id,
            "BeginTime": start_time,
            "EndTime": finish_time,
            "BackupName": log_name,
        })
        print("create success?")
    except exc.UCloudException as e:
        print(e)
    else:
        print("创建日志包成功，日志包名称为：{}".format(log_name))
        print(resp)


def getslowloglist(client, zone, offset=0, limit=50, log_type=None):
    """
    获取日志包列表
    :param client
    :param zone:
    :param offset:
    :param limit:
    :param log_type:
            2 : BINLOG\_BACKUP
            3 : SLOW\_QUERY\_BACKUP
            4 : ERRORLOG\_BACKUP
    :return:
    """
    try:
        resp = client.udb().describe_udb_log_package({
            "Zone": zone,
            "Offset": offset,
            "Limit": limit,
            "Type": log_type

        })
    except exc.UCloudException as e:
        print(e)
    else:
        print("获取slowlog日志列表")
        return resp


def getslowlogid(resp, backup_name, db_id):
    """
    获取slowlog的backupId
    :param resp:
    :param backup_name
    :param db_id
    :return:
    """
    slow_logs_lists = resp["DataSet"]
    print(slow_logs_lists)
    for slow_log in slow_logs_lists:
        if slow_log["BackupName"] == backup_name and slow_log["DBId"] == db_id:
            print("当天slowlog日志包的backupId为：{}".format(slow_log["BackupId"]))
            return slow_log["BackupId"]


def getlogdownloadurl(client, zone, db_id, backup_id):
    """
    返回slowlog日志的下载链接
    :param client
    :param zone:
    :param db_id:
    :param backup_id:
    :return:
    """
    try:
        resp = client.udb().describe_udb_log_backup_url({
            "Zone": zone,
            "DBId": db_id,
            "BackupId": backup_id

        })
    except exc.UCloudException as e:
        print(e)
    else:
        print("下载链接为：{}".format(resp["BackupPath"]))
        return resp["BackupPath"]


def uncompresstgz(file, target_path):
    """
    解压下载后的日志压缩包，tgz
    :param file:
    :return:
    """
    tar = tarfile.open(file)
    file_names = tar.getnames()
    for file_name in file_names:
        tar.extract(file_name, target_path)
    tar.close()


def move(file, dst, new_name):
    """
    移动压缩后的日志，并改名
    :param file:      file to move
    :param dst:       destination directory
    :param new_name   new filename
    :return:
    """
    tmp_location = os.path.join(os.path.dirname(__file__) + "/tmp/")
    file_location = os.path.join(tmp_location, "{}".format(file).replace("tgz", "log").replace("_slowquery", ""))
    shutil.copy(file_location, os.path.join(dst, new_name))


if __name__ == "__main__":
    print(gettimestamp(3))