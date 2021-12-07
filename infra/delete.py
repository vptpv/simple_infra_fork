import requests
import json
from pprint import pprint


def hosts_by_sap(auth, reader):
    messages = []
    for line in reader:
        url = f"{auth.api_domain}/api/hosts?$filter=SapInventory eq '{line['asset_tag']}'"
        r = requests.get(url, cookies=auth.cookies)
        json_1 = json.loads(r.text)[0] if len(json.loads(r.text)) > 0 else {}
        hostid = json_1.get('Id', '')
        hostname = json_1.get('HostName', '')
        if hostid == '':
            messages.append(f"\n{line['asset_tag']} - не в стойке")
            print('`', end='')
        else:
            url = f"{auth.api_domain}/api/hosts/{hostid}"
            payload = {"Task": line['task']}
            r = requests.delete(url, cookies=auth.cookies, data=json.dumps(payload), headers=auth.headers)
            messages.append("{} {} - удалён({})".format(hostname, line['asset_tag'], r.status_code))
            print('.', end='')
    print('\n')
    pprint(messages)


def hosts_by_name(auth, reader):
    messages = []
    for line in reader:
        hostname = line.get('new_name', '')
        url = f"{auth.api_domain}/api/hosts?$filter=HostName eq '{hostname}'"
        r = requests.get(url, cookies=auth.cookies)
        json_1 = json.loads(r.text)[0] if len(json.loads(r.text)) > 0 else {}
        hostid = json_1.get('Id', '')
        if hostid == '':
            messages.append(f"{hostname} - не в стойке")
            print('`', end='')
        else:
            url = f"{auth.api_domain}/api/hosts/{hostid}"
            payload = {"Task": line['task']}
            r = requests.delete(url, cookies=auth.cookies, data=json.dumps(payload), headers=auth.headers)
            messages.append('{} - удалён({})'.format(hostname, r.status_code))
            print('.', end='')
    print('\n')
    pprint(messages)
