import requests, json
from pprint import pprint
from infra import metod, kick
from sheets import write

def to_plan_node(auth, reader):
    list_ = []
    for line in reader:
        string_ = {
            'old_name': metod.get_fat_name(auth.cookies, auth.api_domain, line['new_name']),
            'new_name': line['new_name'],
            'asset_tag': line['asset_tag'],
            'serial': line['serial'],
            'task': line['task']
        }
        list_.append(string_)
    # write.temp(list_)
    pprint(list_)
    make.node_hosts(auth.cookies, list_)
    # write.node_hosts(cookies, auth.api_domain, auth.headers, host)

def switch(auth, reader):
    array = []
    hh = {
        6704: ["edge",150],
        6: ["mngt_row",250],
        662: ["mngt_row",250]
    }
    for line in reader:
        # print("бжж")
        url = f"{auth.api_domain}/api/hosts?$filter=DataCenterRackName eq '{line['new_name'][-4:]}'&$top=1"
        r = requests.get(url, cookies = auth.cookie)
        json_1 = json.loads(r.text)
        try:
            DataCenterId = json_1[0]["DataCenterId"]
            DataCenterRackId = json_1[0]["DataCenterRackId"]
            OrgUnitId = json_1[0]["OrgUnitId"]
            # hostName = str(json_1[0]["HostName"])
        except IndexError:
            print(f"что-то пошло не так")
        else:
            url = f"{auth.api_domain}/api/hosts?$filter=HostName eq '{line['new_name']}'"
            r = requests.get(url, cookies = auth.cookie)
            json_1 = json.loads(r.text)
            # из метки получаем необходимые данные
            url = f"{auth.api_domain}/api/hardware-items?$filter=AccountingId eq '{line['asset_tag']}'"
            r = requests.get(url, cookies = auth.cookie)
            json_2 = json.loads(r.text)
            HardwareModelId = json_2[0]['HardwareModelId']
            # pprint(json_2)
            if len(json_1) == 0:
                print(f"{line['new_name']} - создаём")
                url = f"{auth.api_domain}/api/hosts"
                address = f"{hh[HardwareModelId][1]}.1{line['new_name'][-4:-3]}.5{line['new_name'][-1]}.{int(int(line['new_name'][-3:])/2)}"
                print(address)
                payload = {
                    "TemplateName": "Network", # имя шаблона (тип хоста), обязательное поле
                    "NetworkType": "Switch", # тип устройства, соответствует атрибуту модели HardwareSubType, обязательное поле
                    "OrgUnitId": 199, # для какого проекта создается хост (здесь и ниже используется уникальный идентификатор оргюнита в системе CMDB), обязательное поле
                    "HardwareModelId": HardwareModelId, # уникальный идентификатор модели в системе CMDB, обязательное поле
                    "InstallationTask": line['task'], # задача, по которой устанавливается оборудование, обязательное поле
                    "DataCenterId": DataCenterId, # уникальный идентификатор датацентра в системе CMDB, обязательное поле
                    "DataCenterRackId": DataCenterRackId, # уникальный идентификатор стойки в системе CMDB, обязательное поле
                    "FirstUnit": int(line['old_name']), # номер первого юнита для установки в стойку, обязательное поле
                    "Ip": address, # сетевой адрес устройства; обязательное поле
                    "CustomHostName": line['new_name'], # имя хоста, обязательное поле
                    "NetworkRoles": [hh[HardwareModelId][0]], # список сетевых ролей, обязательное поле для NetworkType = 'Switch'
                }
                r = requests.post(url, cookies = auth.cookie, data=json.dumps(payload), headers = auth.headers)
                if r.status_code == 200:
                    print(f"создан")
                else:
                    print(f"{r.status_code}\t'{json.loads(r.text)['Message']}'")
                    string_2 = {
                        'new_name': line['new_name'],
                        'task': json.loads(r.text)['Message']
                    }
                    array.append(string_2)
                    # print(json.loads(r.text)["Message"])
                    # print(dir(r))
            else:
                print(json_1)
                string_2 = {
                    'new_name': line['new_name'],
                    'task': "что-то не так"
                }
                array.append(string_2)
    pprint(array)
    # rename_hosts(array)

def terminal(auth, reader):
    array = []
    for line in reader:
        url = f"{auth.api_domain}/api/hosts?$filter=DataCenterRackName eq '{line['new_name'][-4:]}'&$top=1"
        r = requests.get(url, cookies = auth.cookie)
        json_1 = json.loads(r.text)
        try:
            DataCenterId = json_1[0]["DataCenterId"]
            DataCenterRackId = json_1[0]["DataCenterRackId"]
            OrgUnitId = json_1[0]["OrgUnitId"]
        except IndexError:
            print(f"что-то пошло не так")
        else:
            url = f"{auth.api_domain}/api/hosts?$filter=HostName eq '{line['new_name']}'"
            r = requests.get(url, cookies = auth.cookie)
            json_1 = json.loads(r.text)
            # из метки получаем необходимые данные
            url = f"{auth.api_domain}/api/hardware-items?$filter=AccountingId eq '{line['asset_tag']}'"
            r = requests.get(url, cookies = auth.cookie)
            json_2 = json.loads(r.text)
            HardwareModelId = json_2[0]['HardwareModelId']
            # pprint(json_2)
            if len(json_1) == 0:
                print(f"{line['new_name']} - создаём... ", end='')
                url = f"{auth.api_domain}/api/hosts"
                payload = {
                    "TemplateName": "Terminal", # имя шаблона (тип хоста), обязательное поле
                    "OrgUnitId": 199, # для какого проекта создается хост (здесь и ниже используется уникальный идентификатор оргюнита в системе CMDB), обязательное поле
                    "HardwareModelId": HardwareModelId, # уникальный идентификатор модели в системе CMDB, обязательное поле
                    "InstallationTask": line['task'], # задача, по которой устанавливается оборудование, обязательное поле
                    "DataCenterId": DataCenterId, # уникальный идентификатор датацентра в системе CMDB, обязательное поле
                    "DataCenterRackId": DataCenterRackId, # уникальный идентификатор стойки в системе CMDB, обязательное поле
                    "FirstUnit": 1, # номер первого юнита для установки в стойку, обязательное поле
                    "Ip": line['old_name'], # сетевой адрес устройства; обязательное поле
                    "CustomHostName": line['new_name'], # имя хоста, обязательное поле
                }
                r = requests.post(url, cookies = auth.cookie, data=json.dumps(payload), headers = auth.headers)
                if r.status_code == 200:
                    print('готово')
                else:
                    print('')
                    print(f"{r.status_code}\t'{json.loads(r.text)['Message']}'")
                    string_2 = {
                        'new_name': line['new_name'],
                        'task': json.loads(r.text)['Message']
                    }
                    array.append(string_2)
            else:
                print(json_1)
                string_2 = {
                    'new_name': line['new_name'],
                    'task': "что-то не так"
                }
                array.append(string_2)
    pprint(array)
    # rename_hosts(array)

def node_hosts(auth, reader):
    array = []
    for line in reader:
        # print("бжж")
        url = f"{auth.api_domain}/api/hosts?$filter=HostName eq '{line['old_name']}'"
        r = requests.get(url, cookies = auth.cookie)
        json_1 = json.loads(r.text)
        try:
            ParentHostId = json_1[0]["Id"]
            DataCenterId = json_1[0]["DataCenterId"]
            OrgUnitId = json_1[0]["OrgUnitId"]
            # hostName = str(json_1[0]["HostName"])
        except IndexError:
            print(f"{line['old_name']} - не в стойке")
        else:
            url = f"{auth.api_domain}/api/hosts"
            payload = {
            # "Task": line['task']
                "TemplateName": "Server",# - имя шаблона (тип хоста), обязательное поле
                "OrgUnitId": OrgUnitId,# - для какого проекта создается хост (здесь и ниже используется уникальный идентификатор оргюнита в системе CMDB), обязательное поле
                "HardwareModelId": 6119,# - уникальный идентификатор модели в системе CMDB, обязательное поле,
                "InstallationTask": line['task'],# - задача, по которой устанавливается оборудование, обязательное поле
                "DataCenterId": DataCenterId,# - идентификатор датацентра в системе CMDB, обязательное поле
                "ParentHostId": ParentHostId,# - идентификатор blade-свича, обязательное поле для blade-сервера
                "BladeSlotList": [1,2,3,4],# - идентификаторы слотов blade-свича, обязательное поле для blade-сервера
                }
            r = requests.post(url, cookies = auth.cookie, data=json.dumps(payload), headers = auth.headers)
            if r.status_code == 200:
                for x in [1,2,3,4]:
                    string_2 = {
                        'old_name': f"icva{line['old_name'][-6:]}0{x}",
                        'new_name': f"{line['new_name'][:-3]}{str(int(line['new_name'][-3:])+x-1)}",
                        'task': line['task']
                    }
                    array.append(string_2)
    pprint(array)
    # rename_hosts(array)

def dwdm(auth, reader):
    array = []
    hh = {
        6704: ["edge",150],
        6: ["mngt_row",250],
        662: ["mngt_row",250]
    }
    for line in reader:
        # print("бжж")
        url = f"{auth.api_domain}/api/hosts?$filter=DataCenterRackName eq '{line['new_name'][-4:]}'&$top=1"
        r = requests.get(url, cookies = auth.cookie)
        json_1 = json.loads(r.text)
        try:
            DataCenterId = json_1[0]["DataCenterId"]
            DataCenterRackId = json_1[0]["DataCenterRackId"]
            OrgUnitId = json_1[0]["OrgUnitId"]
            # hostName = str(json_1[0]["HostName"])
        except IndexError:
            print(f"что-то пошло не так")
        else:
            url = f"{auth.api_domain}/api/hosts?$filter=HostName eq '{line['new_name']}'"
            r = requests.get(url, cookies = auth.cookie)
            json_1 = json.loads(r.text)
            # из метки получаем необходимые данные
            url = f"{auth.api_domain}/api/hardware-items?$filter=AccountingId eq '{line['asset_tag']}'"
            r = requests.get(url, cookies = auth.cookie)
            json_2 = json.loads(r.text)
            
            NetworkType = json_2[0]['HardwareSubTypeName']
            HardwareModelId = json_2[0]['HardwareModelId']
            # pprint(json_2)
            if len(json_1) == 0:
                print(f"{line['new_name']} - создаём")
                url = f"{auth.api_domain}/api/hosts"
                payload = {
                    "TemplateName": "Network", # имя шаблона (тип хоста), обязательное поле
                    "NetworkType": NetworkType, # тип устройства, соответствует атрибуту модели HardwareSubType, обязательное поле
                    "OrgUnitId": 199, # для какого проекта создается хост (здесь и ниже используется уникальный идентификатор оргюнита в системе CMDB), обязательное поле
                    "HardwareModelId": HardwareModelId, # уникальный идентификатор модели в системе CMDB, обязательное поле
                    "InstallationTask": line['task'], # задача, по которой устанавливается оборудование, обязательное поле
                    "DataCenterId": DataCenterId, # уникальный идентификатор датацентра в системе CMDB, обязательное поле
                    "DataCenterRackId": DataCenterRackId, # уникальный идентификатор стойки в системе CMDB, обязательное поле
                    "FirstUnit": int(line['old_name']), # номер первого юнита для установки в стойку, обязательное поле
                    "Ip": f"166.1{int(line['new_name'][5:6])}.2{int(line['new_name'][4:5])}.{int(line['new_name'][-2:])}", # сетевой адрес устройства; обязательное поле
                    "CustomHostName": line['new_name'], # имя хоста, обязательное поле
                    # "NetworkRoles": [hh[HardwareModelId][0]], # список сетевых ролей, обязательное поле для NetworkType = 'Switch'
                }
                r = requests.post(url, cookies = auth.cookie, data=json.dumps(payload), headers = auth.headers)
                if r.status_code == 200:
                    print(f"создан")
                else:
                    print(f"{r.status_code}\t'{json.loads(r.text)['Message']}'")
                    string_2 = {
                        'new_name': line['new_name'],
                        'task': json.loads(r.text)['Message']
                    }
                    array.append(string_2)
                    # print(json.loads(r.text)["Message"])
                    # print(dir(r))
            else:
                print(json_1)
                string_2 = {
                    'new_name': line['new_name'],
                    'task': "что-то не так"
                }
                array.append(string_2)
    pprint(array)
