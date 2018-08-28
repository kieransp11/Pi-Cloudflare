import urllib.request
import urllib.parse
from typing import Dict
import json
import os

headers = {
    "Content-Type": "application/json"
}


def get_ip() -> str:
    """
    :return: IP address
    """
    return urllib.request.urlopen("https://api.ipify.org").read().decode('utf-8')


def get_zone(domain_name: str) -> str:
    """
    :param domain_name: a domain name, "example.com"
    :return: zone id for domain
    """
    url = "https://api.cloudflare.com/client/v4/zones"
    values = {
        "name": domain_name
    }

    url_values = urllib.parse.urlencode(values)
    full_url = url + '?' + url_values
    req = urllib.request.Request(url=full_url, headers=headers)

    with urllib.request.urlopen(req) as response:
        zone_id = json.loads(response.read().decode('utf-8'))['result'][0]['id']

    return zone_id


def get_dns_record(domain: str, hostname="", record_type="A") -> Dict:
    """
    :param domain: domain to get dns record for "example.com"
    :param hostname: hostname to retrieve DNS record for  "www"
    :param record_type: type of DNS record to return
    :return: dns record of hostname and type requested
    """
    zone = get_zone(domain)
    url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records" % zone
    name = domain if hostname == "" else hostname+"."+domain

    values = {
        "name": name,
        "type": record_type
    }

    url_values = urllib.parse.urlencode(values)
    full_url = url + '?' + url_values
    req = urllib.request.Request(url=full_url, headers=headers)

    with urllib.request.urlopen(req) as response:
        dns_record = json.loads(response.read().decode('utf-8'))['result']

    if not dns_record:
        return {}
    else:
        return dns_record[0]


def point_dns_record(record: Dict, ip_address: str) -> bool:
    """
    :param record: Updates the dns record to point to the given IP address
    :param ip_address: IP to point to
    :return:
    """
    url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records/%s" % (record["zone_id"], record["id"])
    body = {
        "type": record["type"],
        "name": record["name"],
        "content": ip_address
    }

    params = json.dumps(body).encode('utf8')
    req = urllib.request.Request(url, data=params, headers=headers, method="PUT")
    with urllib.request.urlopen(req) as response:
        success = json.loads(response.read().decode('utf-8'))["success"]

    return success


def point_sub_domain_here(domain: str, sub_domain="", record_type="A") -> bool:
    """
    :param domain: domain to point here
    :param sub_domain: sub-domain of domain to point here
    :param record_type: record type of DNS entry updating
    :return: if update was successful
    """
    public_ip = get_ip()
    record = get_dns_record(domain, sub_domain, record_type)

    if record:
        return point_dns_record(record, public_ip)
    else:
        raise Exception("No such DNS record for %s.%s" % (sub_domain, domain))


def main():
    global headers

    path = os.path.dirname(os.path.realpath(__file__))

    # Load the config file
    with open(path+'/config.json', 'r') as f:
        config = json.load(f)

    ip = get_ip()

    # if IP hasn't changed no need to do any updates
    if ip == config["ip"]:
        exit()

    # Retrieve authentication headers
    headers.update(config["headers"])

    # Start pointing specified domains here
    domains = config["domains"]
    for domain in domains:
        sub_domains = domains[domain]
        for sub_domain in sub_domains:
            record_type = sub_domains[sub_domain]
            if not point_sub_domain_here(domain, sub_domain, record_type):
                raise Exception("Pointing sub-domain failed: %s %s %s" % (sub_domain, domain, record_type))

    # update config file with new IP
    config["ip"] = ip
    with open("config.json", "w") as f:
        json.dump(config, f)


main()
