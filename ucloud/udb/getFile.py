# coding: utf-8
import os
import wget
import time
import re
import logging
import datetime
from ucloud.client import Client
from getApiCsv import ssh_scp_get
from getSlowLog import gettimestamp, createslowlog, getlogdownloadurl, getslowloglist, getslowlogid, move, uncompresstgz 
from dingding import ding_url, ding_text
import sys


# [常量]
DOMAIN = "file.yytrax.com"
DATE = datetime.datetime.date(datetime.datetime.now())
DOWNLOAD_PATH = os.path.dirname(__file__)
# 测试钉钉API
PRIVATE_DING_API = "xxx"
# 钉钉预警群
DING_API = "https://oapi.dingtalk.com/robot/xxx"

# API CSV 配置
#PORT = 22
USER = 'root'

date = time.strftime("%Y%m%d")
#api_filename = "/var/log/nginx/api_ec_youmobi_com.access_log-{date}.csv".format(date=date)
#local_filename = os.path.join(os.path.join(DOWNLOAD_PATH, "api"), "api_ec_youmobi_com.access_log-{date}.csv".format(date=date))



# Slowlog 配置(Ucloud API接口)
REGION = "us-ca"
PROJECT_ID = "org-27257"
PUBLIC_KEY = "xxx"
PRIVATE_KEY = "xxx"
DBID = "xxx"
ZONE = "us-ca-01"
DIR = "/data/users/dylan/slow/"


# 添加日志
log_path = "/data/users/dylan/log/event.log"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

while logger.hasHandlers():
    for i in logger.handlers:
        logger.removeHandler(i)

formatter = logging.Formatter("%(asctime)s - %(name)s : %(lineno)d - %(message)s")
fh = logging.FileHandler(log_path, encoding="utf-8")
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

# 获取api csv
#try:
#    logger.info("正在获取今天api csv文件")
#    ssh_scp_get(ip=IP, port=PORT, user=USER, password=PASSWORD, remote_file=api_filename, local_file=local_filename)
#    # zero_size_warning(local_filename)
#except Exception as e:
#    logger.error(e)
#else:
#    logger.info("api csv文件已保存")

# 获取slowlog
try:    
    logger.info("开始执行slowlog日志打包下载")
    client = Client({
        "region": REGION,
        "project_id": PROJECT_ID,
        "public_key": PUBLIC_KEY,
        "private_key": PRIVATE_KEY,
    })

    start_time, end_time = gettimestamp(2)
    print(start_time, end_time)
    log_name = "slowlog-{}.log".format(date)

    # 慢日志包
    createslowlog(client, db_id=DBID, start_time=start_time, finish_time=end_time, log_name=log_name)
    resp = getslowloglist(client, zone=ZONE, offset=0, limit=50, log_type=3)
    logger.info("resp: {}".format(resp))
    # 获取慢日志包的ID
    package_id = getslowlogid(resp, backup_name=log_name, db_id=DBID)
    logger.info("当天的slowlog包id为: {}".format(package_id))
    # 获取慢日志包的下载url
    url = getlogdownloadurl(client, zone=ZONE, db_id=DBID, backup_id=package_id)
    print("debuging")
    logger.info("slowlog下载url为：{}".format(url))
    # Ucloud打包日志需要等一会，这里阻塞60秒
    time.sleep(100)
    downloaded_filename = re.split(r'[/?]', url)[4]
    wget.download(url, out=DOWNLOAD_PATH)
    uncompresstgz(os.path.join(DOWNLOAD_PATH, downloaded_filename), DOWNLOAD_PATH)
    move(downloaded_filename, dst=DIR, new_name="ymcore-slowlog-{}.log".format(date))
    #zero_size_warning(os.path.join(DOWNLOAD_PATH, downloaded_filename))
except Exception as e:
    logger.error(e)
    ding_text(PRIVATE_DING_API, "下载当天slowlog日志失败，请检查ucloud api密钥对是否失效或者打包时间是否足够长")
else:
    logger.info("下载当天slowlog日志成功")
    # 发送链接到钉钉群
    #api_download_url = "http://{domain}/api/api_ec_youmobi_com.access_log-{date}.csv".format(domain=DOMAIN, date=date)
    slow_download_url = "http://{domain}/slow/ymcore-slowlog-{date}.log".format(domain=DOMAIN, date=date)
    content = "{DATE} slowlog文件:\n{slow_url}".format(DATE=DATE, slow_url=slow_download_url)
    #ding_text(DING_API, content)