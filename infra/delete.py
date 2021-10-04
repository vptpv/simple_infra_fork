import requests, json
from pprint import pprint
from infra import make

def hosts_by_sap(auth, reader):
    messages = []
    for line in reader:
        url = f"{auth.api_domain}/api/hosts?$filter=SapInventory eq '{line['asset_tag']}'"
        r = requests.get(url, cookies = auth.cookies)
        json_1 = json.loads(r.text)
        try:
            hostId = str(json_1[0]["Id"])
            hostName = str(json_1[0]["HostName"])
        except IndexError:
            messages.append(f"\n{line['asset_tag']} - не в стойке")
            print('`', end='')
        else:
            url = f"{auth.api_domain}/api/hosts/{hostId}"
            payload = {"Task": line['task']}
            r = requests.delete(url, cookies = auth.cookies, data=json.dumps(payload), headers=auth.headers)
            messages.append(f"{hostName} {line['asset_tag']} - удалён")
            print('.', end='')
    print('\n')
    pprint(messages)

def hosts_by_name(auth, reader):
    messages = []
    for line in reader:
        url = f"{auth.api_domain}/api/hosts?$filter=HostName eq '{line['new_name']}'"
        r = requests.get(url, cookies = auth.cookies)
        json_1 = json.loads(r.text)
        try:
            hostId = str(json_1[0]["Id"])
            hostName = str(json_1[0]["HostName"])
        except IndexError:
            messages.append(f"{line['new_name']} - не в стойке")
            print('`', end='')
        else:
            url = f"{auth.api_domain}/api/hosts/{hostId}"
            payload = {"Task": line['task']}
            r = requests.delete(url, cookies = auth.cookies, data=json.dumps(payload), headers=auth.headers)
            messages.append(f"{hostName} - удалён")
            print('.', end='')
    print('\n')
    pprint(messages)
