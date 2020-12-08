import requests
import json
import argparse


HEADERS = {
    "X-Auth-Key": "xxx",
    "X-Auth-Email": "dylan@youmobi.com",
    "Content-Type": "application/json"
}
API = "https://api.cloudflare.com/client/v4/"


def getAllDomains():
    result = requests.get(API + "zones?per_page=50", headers=HEADERS).json()['result']
    domains = {}
    for domain in result:
        domains[domain['name']] = {
            "name": domain['name'],
            "id": domain['id']
        }
    return domains

def getOneDomainId(domains, domain_name):
    return domains[domain_name]['id']

def getDnsRecord(domain_id):
    """GET zones/:zone_identifier/dns_records"""
    request_url = API + "zones/%s/dns_records?per_page=50&type=A" % domain_id
    dns_records = requests.get(request_url, headers=HEADERS).json()['result']
    for record in dns_records:
        print("name: %s, type: %s, value: %s" % (record['name'], record['type'], record['content']))

def createDnsRecord(domain_id, name, content):
    """POST zones/:zone_identifier/dns_records"""
    request_url = API + "zones/%s/dns_records?per_page=50&type=A" % domain_id
    data = {
        "type": "A",
        "name": name,
        "content": content,
        "ttl": 120,
        "priority": 10,
        "proxied": True
    }
    response = requests.post(request_url, headers=HEADERS, json=data)
    print(response.content)

def createBatchDnsRecords(*domain_id):
    # To do
    pass

def deleteDnsRecord():
    """DELETE zones/:zone_identifier/dns_records/:identifier"""
    # have to do?
    pass


if __name__ == "__main__":
    domains = getAllDomains()

    parser = argparse.ArgumentParser()
    parser.add_argument("--domain", "-d", help="domain name like 'example.com'", required=True)

    args = parser.parse_args()
    domain = args.domain
    domain_id = getOneDomainId(domains, domain)

    names = ["cn", "www", "my", "th", "tw", "sg", "@"]
    for name in names:
        createDnsRecord(domain_id, name, "xxx")