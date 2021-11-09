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
        r = requests.get(url, cookies = auth.cookies)
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
            r = requests.get(url, cookies = auth.cookies)
            json_1 = json.loads(r.text)
            # из метки получаем необходимые данные
            url = f"{auth.api_domain}/api/hardware-items?$filter=AccountingId eq '{line['asset_tag']}'"
            r = requests.get(url, cookies = auth.cookies)
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
                r = requests.post(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
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
        r = requests.get(url, cookies = auth.cookies)
        json_1 = json.loads(r.text)
        try:
            DataCenterId = json_1[0]["DataCenterId"]
            DataCenterRackId = json_1[0]["DataCenterRackId"]
            OrgUnitId = json_1[0]["OrgUnitId"]
        except IndexError:
            print(f"что-то пошло не так")
        else:
            url = f"{auth.api_domain}/api/hosts?$filter=HostName eq '{line['new_name']}'"
            r = requests.get(url, cookies = auth.cookies)
            json_1 = json.loads(r.text)
            # из метки получаем необходимые данные
            url = f"{auth.api_domain}/api/hardware-items?$filter=AccountingId eq '{line['asset_tag']}'"
            r = requests.get(url, cookies = auth.cookies)
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
                r = requests.post(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
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
        r = requests.get(url, cookies = auth.cookies)
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
            r = requests.post(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
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
        r = requests.get(url, cookies = auth.cookies)
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
            r = requests.get(url, cookies = auth.cookies)
            json_1 = json.loads(r.text)
            # из метки получаем необходимые данные
            url = f"{auth.api_domain}/api/hardware-items?$filter=AccountingId eq '{line['asset_tag']}'"
            r = requests.get(url, cookies = auth.cookies)
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
                r = requests.post(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
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

def office_switch(auth, reader): # свичи в офис
    array = []
    array_ok = []
    hh = {
        6704: ["edge",150],
        6: ["mngt_row",250],
        662: ["mngt_row",250]
    }
    address = ''
    for line in reader:
        if line.get('unit', 'хуй') == 'хуй':
            line.update({'row': line['new_name'][3:6]})
            line.update({'rack': line['new_name'][3:7]})
        # чешем адрес
        if address == '':
            address = f"182.1{int(int(line['task'][-4:-3])/2)}.{int(int(line['task'][-4:-3])/4)}.{int(int(line['task'][-3:])/20)}"
        address = address.split('.')
        address.append(str(int(address.pop(3))+1))
        address = '.'.join(address)
        # print(address)
        payload = {
            'TemplateName': 'хуй', # имя шаблона (тип хоста), обязательное поле
            'NetworkType': 'хуй', # тип устройства, соответствует атрибуту модели HardwareSubType, обязательное поле
            'OrgUnitId': 'хуй', # для какого проекта создается хост (здесь и ниже используется уникальный идентификатор оргюнита в системе CMDB), обязательное поле
            'HardwareModelId': 'хуй', # уникальный идентификатор модели в системе CMDB, обязательное поле
            'InstallationTask': line['task'], # задача, по которой устанавливается оборудование, обязательное поле
            'DataCenterId': 'хуй', # уникальный идентификатор датацентра в системе CMDB, обязательное поле
            'DataCenterRackId': 'хуй', # уникальный идентификатор стойки в системе CMDB, обязательное поле
        }
        if line['new_name'][:3] == 'eva':
            url = "{}/api/hosts?$filter=DataCenterRackName eq '{}'&$top=1".format(
                auth.api_domain,
                line['rack']
                )
            # print(url)
            r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
            line.update({'unit': metod.position(line['new_name'], json_1[0].get('DataCenterName', 'хуй'))})
            payload.update({'HostQuantity': 1})
            payload.update({'DataCenterRowId': json_1[0].get('DataCenterRowId', 'хуй')})
            payload.update({'DataCenterRackId': json_1[0].get('DataCenterRackId', 'хуй')})

        else:
            payload.update({'CustomHostName': line['new_name']})
            if line['new_name'].split('-')[0].upper() == 'FT':
                loca_tion = line['new_name'].split('-')[1].upper()
            else:
                loca_tion = line['new_name'].split('-')[0].upper()
            url = "{}/api/hosts?$filter=DataCenterLocation eq '{}' and DataCenterRowName eq '{}'&$top=1".format(
                auth.api_domain,
                loca_tion,
                line['row'],
                )
            r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
        payload.update({'FirstUnit': int(line['unit'])})
        if len(json_1) == 0:
            # получаем номер локации
            url = "{}/api/data-center-locations?$filter=Name eq '{}'".format(
                auth.api_domain,
                line['new_name'].split('-')[0].upper()
                )
            r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
            # получаем номер нужного цода в локации
            url = "{}/api/data-center-locations/{}/data-centers".format(
                auth.api_domain,
                json_1[0].get('Id', 'хуй')
                )
            r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
            # пишем
            payload.update({'DataCenterId': json_1[0].get('Id', 'хуй')})
            # получаем ряд
            url = "{}/api/data-centers/{}/rows?$top=1".format(
                auth.api_domain,
                json_1[0].get('Id', 'хуй')
                )
            r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
            # получаем стойку
            url = "{}/api/data-centers/rows/{}/racks?$filter=Name eq '{}'".format(
                auth.api_domain,
                json_1[0].get('Id', 'хуй'),
                line['rack']
                )
            r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
            # пишем
            payload.update({'OrgUnitId': json_1[0].get('OrgUnits', 'хуй')[0]})
        else:
            payload.update({'DataCenterId': json_1[0].get('DataCenterId', 'хуй')})
            url = "{}/api/data-centers/rows/{}/racks?$filter=Name eq '{}'".format(
                auth.api_domain,
                json_1[0].get('DataCenterRowId', 'хуй'),
                line['rack']
                )
            r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
            # пишем
            payload.update({'OrgUnitId': json_1[0]['OrgUnits'][0]})

        if payload['DataCenterId'] == 'хуй' or payload['OrgUnitId'] == 'хуй':
            print(f"что-то не так с локацией")
        else:
            url = "{}/api/data-centers/{}/rows".format(
                auth.api_domain,
                payload['DataCenterId']
                )
            # print(url)
            r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
            for i in json_1:
                if i.get('Name', 'хуй') == line['row'].upper() and payload['DataCenterRackId'] == 'хуй':
                    payload.update({'DataCenterRackId': i['RackIds'][int(line['rack'].split(' ')[0][-2:])-1]})
            if payload['DataCenterRackId'] == 'хуй':
                print(f"что-то не так cо стойкой")
            else:
                url = "{}/api/hosts?$filter=HostName eq '{}'".format(
                    auth.api_domain,
                    line['new_name']
                    )
                r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
                if len(json_1) == 0:
                    # из метки получаем необходимые данные
                    url = "{}/api/hardware-items?$filter=AccountingId eq '{}'".format(
                        auth.api_domain,
                        line['asset_tag']
                        )
                    r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
                    payload.update({'TemplateName': json_1[0]['HardwareTypeName']})
                    payload.update({'NetworkType': json_1[0]['HardwareSubTypeName']})
                    payload.update({'HardwareModelId': json_1[0]['HardwareModelId']})
                    payload.update({'BalanceUnitId': int(json_1[0]['BalanceUnitId'])})
                    if payload.get('TemplateName') == 'Network':
                        payload.update({'Ip':address})
                        # чекаем атрибуты
                        url = "{}/api/hardware-models?$top=1&$expand=Attributes&$filter=Name eq '{}'".format(
                            auth.api_domain,
                            json_1[0]['HardwareModelName']
                            )
                        r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
                        # вынимаем роль
                        for i in json_1[0]['Attributes']:
                            if i.get('Name', 'хуй') == 'Network Roles':
                                payload.update({'NetworkRoles': [i.get('TextValue').split(',')[0].strip()]})
                    if payload.get('TemplateName') == 'Blade':
                        # по хорошему стоит проверить ноды на складе но пока так
                        payload.update({'BladeServerHardwareModelId': 6119})
                    # print(f"{line['new_name']}\t{line['unit']}\t")
                    # pprint(payload)
                    print(f"{line['new_name']}\t{line['unit']}\t",end='')
                    url = f"{auth.api_domain}/api/hosts"
                    r = requests.post(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
                    if r.status_code == 200:
                        old_name = json.loads(r.text)[0]['Name']
                        print(old_name)
                        # print(f"создан")
                        array_ok.append([old_name, line['new_name']])
                    # elif r.status_code == 400 and json.loads(r.text)['Message'].split(' ')[0] == 'Another':
                    #     print(json.loads(r.text)['Message'])
                        # sleep()
                        # r = requests.post(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
                    else:
                        print(f"{r.status_code}\t'{json.loads(r.text)['Message']}'")
                        pprint(payload)
                        string_2 = {
                            'new_name': line['new_name'],
                            'task': json.loads(r.text)['Message']
                        }
                        array.append(string_2)
                else:
                    print(f"{line['new_name']}\tуже есть")
                    string_2 = {
                        'new_name': line['new_name'],
                        'task': "уже есть"
                    }
                    array.append(string_2)
    pprint(array)
    write.temp(array_ok)
    # rename_hosts(array)
