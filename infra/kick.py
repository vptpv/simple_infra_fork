import requests, json, datetime, time
from sheets import write
from pprint import pprint

def rename_hosts(auth, reader):
    for line in reader:
        url = f"{auth.api_domain}/api/hosts?$filter=HostName eq '{line['old_name']}'"
        if line.get('status_code', 0) != 0:
            json_1 = []
            tic = time.perf_counter()
            while len(json_1) == 0:
                r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
                time.sleep(1)
            toc = time.perf_counter()
            print(str(toc-tic))

            url = f"{auth.api_domain}/api/hosts/{line['old_name']}/name/{line['new_name']}"
            payload = {"Task": line['task']}
            r = requests.put(url, cookies = auth.cookies, data=json.dumps(payload))
            print(r)
        else:
            r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
            try:
                hostId = str(json_1[0]["Id"])
                hostName = str(json_1[0]["HostName"])
            except IndexError:
                print(f"{line['old_name']} - не в стойке")
            else:
                url = f"{auth.api_domain}/api/hosts/{line['old_name']}/name/{line['new_name']}"
                payload = {"Task": line['task']}
                r = requests.put(url, cookies = auth.cookies, data=json.dumps(payload))
                print(f"{line['old_name']}\t{line['new_name']}\t{line['task']}")

def rename_sap(auth, reader):
    for line in reader:
        url = f"{auth.api_domain}/api/hosts?$filter=SapInventory eq '{line['asset_tag']}'"
        r = requests.get(url, cookies = auth.cookies)
        json_1 = json.loads(r.text)
        try:
            hostId = str(json_1[0]["Id"])
            hostName = str(json_1[0]["HostName"])
        except IndexError:
            print(f"{line['asset_tag']} - не в стойке")
        else:
            url = f"{auth.api_domain}/api/hosts/{hostName}/name/{line['new_name']}"
            payload = {"Task": line['task']}
            r = requests.put(url, cookies = auth.cookies, data=json.dumps(payload))
            print(f"{hostName}\t{line['new_name']}\t{line['task']}")

def set_sap_id(auth, reader):
    url = f"{auth.api_domain}/api/hosts/accounting/batch-change"
    payload = []
    for line in reader:
        if line.get('status_code', 0) != 0:
            pair = {
                "HostName": line['old_name'],
                "AccountingId": line['asset_tag']
            }
        else:
            pair = {
                "HostName": line['new_name'],
                "AccountingId": line['asset_tag']
            }
        payload.append(pair)
    r = requests.post(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
    if r.status_code == 200:
        print(f"вроде присвоились")
    else:
        print(f"{r.status_code}\t'{json.loads(r.text)['Message']}'")

def add_sn(auth, reader): # вроде робит
    errors = []
    for line in reader:
        data = {
            'sapid': f"$filter=AccountingId eq '{line['asset_tag']}'",
            'serial': f"$filter=SerialNumber eq '{line['serial']}'"
        }
        url = f"{auth.api_domain}/api/hardware-items?"
        r_ser = requests.get(url+data['serial'], cookies = auth.cookies)
        json_ser = json.loads(r_ser.text)
        try:
            # hostId = str(json_1[0]["Id"])
            AccountingId = str(json_ser[0].get('AccountingId','хуй'))
        except KeyError:
            print(f"\n{line['asset_tag']}\t{line['serial']}\tчто блядь?")
            string = [line['asset_tag'],line['serial'],'что блядь?']
            errors.append(string)
        except IndexError:
            r_sap = requests.get(url+data['sapid'], cookies = auth.cookies)
            json_sap = json.loads(r_sap.text)
            try:
                SerialNumber = str(json_sap[0]['SerialNumber'])
            except IndexError:
                print(f"\n{line['asset_tag']}\t\tотсутствует железка")
                string = [line['asset_tag'],line['serial'],'отсутствует железка']
                errors.append(string)
            else:
                if json_sap[0].get('SerialNumber', '0') is None:
                    url = f"{auth.api_domain}/api/accountings/{line['asset_tag'].upper()}/serial/{line['serial'].upper()}"
                    r = requests.put(url, cookies = auth.cookies)
                    if r.status_code == 200:
                        print('^', end='')
                        # print(f"\n{str(json_sap[0]['AccountingId'])}\t{line['serial']}\tстало хорошо")
                        strong = f"{str(json_sap[0]['AccountingId'])}\t{line['serial']}\tстало хорошо"
                    else:
                        print(f"\n{line['asset_tag']}\t\tне дружелюбный ответ")
                        string = [line['asset_tag'],line['serial'],'не дружелюбный ответ']
                        errors.append(string)
                else:
                    print(f"\n{line['asset_tag']}\t->{str(json_sap[0]['SerialNumber'])}<-\t{line['serial']}\tуже есть другой серийник")
                    string = [line['asset_tag'],line['serial'],str(json_sap[0]['SerialNumber'])]
                    errors.append(string)
                # жуткий костыль
                # elif json_sap[0].get('SerialNumber', '0') == 'AC1F6B92B535' and json_sap[0].get('AccountingId', '0') == 'SRV358743':
                #     url = f"{auth.api_domain}/api/accountings/{line['asset_tag'].upper()}/serial/{line['serial'].upper()}"
                #     r = requests.put(url, cookies = auth.cookies)
                #     if r.status_code == 200:
                #         print(f"{str(json_sap[0]['AccountingId'])}\t{line['serial']}\tстало хорошо")
        else:
            if AccountingId == line['asset_tag'].upper():
                print('.', end='')
                # print(f"{AccountingId}\t{str(json_ser[0]['SerialNumber'])}\tбыло хорошо")
                strong = f"{AccountingId}\t{str(json_ser[0]['SerialNumber'])}\tбыло хорошо"
            else:
                print(f"{line['asset_tag']}\t{str(json_ser[0]['SerialNumber'])}\tметка не соответствует")
                string = [line['asset_tag'],line['serial'],'метка не соответствует']
                errors.append(string)
    pprint(errors)
    write.temp(errors)

def hard_add_sn(auth, reader): # вроде робит
    errors = []
    for line in reader:
        data = {
            'sapid': f"$filter=AccountingId eq '{line['asset_tag']}'",
            'serial': f"$filter=SerialNumber eq '{line['serial']}'"
        }
        url = f"{auth.api_domain}/api/hardware-items?"
        r_sap = requests.get(url+data['sapid'], cookies = auth.cookies)
        json_sap = json.loads(r_sap.text)
        try:
            AccountingId = str(json_sap[0].get('AccountingId','хуй'))
        except KeyError:
            print(f"{line['asset_tag']}\t{line['serial']}\tчто блядь?")
            string = [line['asset_tag'],line['serial'],'что блядь?']
            errors.append(string)
        except IndexError:
            print(f"{line['asset_tag']}\t{line['serial']}\tнетю")
            string = [line['asset_tag'],line['serial'],'нетю']
            errors.append(string)
        else:
            url = f"{auth.api_domain}/api/accountings/{line['asset_tag'].upper()}/serial/{line['serial'].upper()}"
            r = requests.put(url, cookies = auth.cookies)
            if r.status_code == 200:
                print(f"{str(json_sap[0]['AccountingId'])}\t{line['serial']}\tисправил жоско")
                strong = f"{str(json_sap[0]['AccountingId'])}\t{line['serial']}\tстало хорошо"
            else:
                print(url)
                print(f"{line['asset_tag']}\t{r.status_code}\t{json.loads(r.text)['Message']}")
                string = [line['asset_tag'],line['serial'],json.loads(r.text)['Message']]
                errors.append(string)
    pprint(errors)

def change_mac_addresses(auth, reader):
    for line in reader:
        if line['old_name'][2] == ':':
            mac = line['old_name']
        else:
            mac = '{}:{}:{}:{}:{}:{}'.format(
                line['old_name'][0:2],
                line['old_name'][2:4],
                line['old_name'][4:6],
                line['old_name'][6:8],
                line['old_name'][8:10],
                line['old_name'][10:],
                )

        url = f"{auth.api_domain}/api/accountings/{line['asset_tag']}/interfaces"
        payload = [
                {
                    "Name": "mngt",
                    "HardwareAddress": mac
                }
            ]
        r = requests.put(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
        # r = requests.delete(url, cookies = auth.cookies, headers = auth.headers)
        if r.status_code != 200:
            print('')
            print(f"{r.status_code}\t'{json.loads(r.text)['Message']}'")
        else:
            print('.', end='')
    print('\n\tэрон дон доне')


def change_network_roles(auth, reader):
    hh = {
        6704: ["edge",150],
        6: ["mngt_row",240],
        662: ["mngt_row",250]
    }
    for line in reader:
        url = f"{auth.api_domain}/api/hosts?$filter=HostName eq '{line['new_name']}'"
        r = requests.get(url, cookies = auth.cookies)
        json_1 = json.loads(r.text)
        # получаем необходимые данные
        hostId = json_1[0]['Id']
        HardwareModelId = json_1[0]['HardwareModelId']
        url = f"{auth.api_domain}/api/hosts/{hostId}/change-network-roles"
        payload = {"Roles": [{"Name": hh[HardwareModelId][0],"IsPrimary": True}]}
        r = requests.put(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
        if r.status_code != 200:
            print(f"{r.status_code}\t'{json.loads(r.text)['Message']}'")

# def set_work_status(auth, reader):
#     for line in reader:
#         url = f"{auth.api_domain}/api/hosts?$filter=HostName eq '{line['new_name']}'"
#         r = requests.get(url, cookies = auth.cookies)
#         json_1 = json.loads(r.text)
#         try:
#             hostId = str(json_1[0]["Id"])
#         except IndexError:
#             print(f"{line['new_name']} - не в стойке")
#         else:
#             url = f"{auth.api_domain}/api/hosts/{hostId}/set-work-status"
#             # url = f"{auth.api_domain}/api/hosts/{hostId}/set-production-status"
#             day_ta = datetime.datetime.today() + datetime.timedelta(days=1)
#             # print(day_ta.strftime("%Y-%m-%d"))
#             payload = {"DueDate": f"{day_ta.strftime('%Y-%m-%d')}","WorkTask": line['task']}
#             r = requests.post(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
#             # r = requests.post(url, cookies = auth.cookies, headers = auth.headers)
#             if r.status_code != 200:
#                 print(f"{line['new_name']}\t{r.status_code}\t'{json.loads(r.text)['Message']}'")
