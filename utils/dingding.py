import requests
import json


headers = {"Content-Type": "application/json"}

def ding_text(apiurl, content):
    msg = {"msgtype": "text", "text":{"content": content}}
    requests.post(apiurl, headers=headers, data=json.dumps(msg))

def ding_url(apiurl, title, text, url):
    msg = {"msgtype": "link", 
           "link": {
                "text": text,
                "title": title,
                "messageUrl": url
        }
    }
    requests.post(apiurl, headers=headers, data=json.dumps(msg))