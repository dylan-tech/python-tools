#!/usr/bin/python3.6
import time
import os
import argparse
import pprint
import requests
import json


# 相差率阀值
WARNING_VALUE = 0.5

# dingding API
dingding_api = "xxx"
headers = {"Content-Type": "application/json"}


def ding_text(apiurl, content):
    msg = {"msgtype": "text", "text": {"content": content}}
    requests.post(apiurl, headers=headers, data=json.dumps(msg))


def get_datetimes(start=0, end=0):
    """
    param: n    时间周期
    """
    timestamp = time.time()
    minutes = []
    for i in range(start, end):
        # timeArray = time.localtime(timestamp - 60 * i)
        
        timeArray = time.localtime(timestamp - 60 * i - 22 * 60 * 62)  # 开发机测试
        minutes.append(time.strftime("%d/%b/%Y:%H:%M", timeArray))
    return minutes


def get_filter_condition(datetimeArray):
    return "|".join(datetimeArray)


def get_result(condition, filename):
    cmd = """egrep '{condition}' {filename}""".format(condition=condition, filename=filename) + """| awk '{a[$2]+=1;} END {for(i in a){print a[i]" "i;}}'"""
    result = os.popen(cmd)
    return result.readlines()


def result_split(element):
    count = int(element.split()[0])
    domain = element.split()[1].replace("\n", "")
    return domain, count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', "--file", help="文件", nargs="+")
    args = parser.parse_args()
    for logfile in args.file:
        CountTimes = {
            "previous": {},
            "after": {},
        }
        filename = logfile
        # 前一段时间的记录次数
        previous_filter_condition = get_filter_condition(get_datetimes(10, 20))
        previous_result = get_result(previous_filter_condition, filename)
        for result in previous_result:
            domain, count = result_split(result)
            CountTimes['previous'][domain] = count

        # 后一段时间的记录次数
        after_filter_condition = get_filter_condition(get_datetimes(0, 10))
        after_result = get_result(after_filter_condition, filename)
        for result in after_result:
            domain, count = result_split(result)
            CountTimes['after'][domain] = count

   
        domains = set()
        for domain in CountTimes['previous'].keys():
            domains.add(domain)

        for domain in CountTimes['after'].keys():
            domains.add(domain)

        # 判断条件
        for domain in domains:
            # 前段时间没该域名，跳过
            if domain not in CountTimes['previous'].keys():
                continue
            # 后段时间没该域名，则赋值为0
            if domain not in CountTimes['after'].keys():
                CountTimes['after'][domain] = 0
            # 前段时间域名次数不超过20，跳过
            if CountTimes['previous'][domain] < 20:
                continue
            # 后段时间比前段时间多，跳过
            if CountTimes['after'][domain] > CountTimes['previous'][domain]:
                continue
            # 前后两段时间次数相差率不超过50%，跳过
            diff = abs(CountTimes['previous'][domain] - CountTimes['after'][domain])
            percentage = float(diff / CountTimes['previous'][domain])
            if percentage < WARNING_VALUE:
                continue
            diff_percentage = "%.2f" % (percentage * 100) + "%"
            message = "请求域名：{}\n前0-10分钟请求次数：{}次\n前10-20分钟请求次数：{}次\n相差次数：{}次\n相差率： {}\n".format(domain, CountTimes['previous'][domain], CountTimes['after'][domain], diff, diff_percentage)
            ding_text(dingding_api, message)