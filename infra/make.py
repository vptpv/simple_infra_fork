import requests, json
from pprint import pprint
from infra import metod, kick, to_plan
from gsheets import write

def get_parent_for_nodes(auth, reader):
    list_ = []
    for line in reader:
        line.update({'fat_name': metod.get_fat_name(line['new_name'])})
        line,sap_id = to_plan.get_data_from_id(auth, line['asset_tag'], line)
        line,group = to_plan.get_data_from_host(auth, line['new_name'], line)
        list_.append(line)
    hh = {}
    for line in list_:
        if hh.get(line['fat_name'], 0) == 0:
            hh.update({line['fat_name']: {}})
            hh[line['fat_name']].update({'nodes':[line]})
            FreeSlots,ParentHostId = check_blade(auth, line)
            hh[line['fat_name']].update({
                'payload':{
                    'TemplateName': line['TemplateName'],
                    'OrgUnitId': line['OrgUnitId'],
                    'DataCenterId': line['DataCenterId'],
                    'InstallationTask': line['task'],
                    'HardwareModelId': line['HardwareModelId'],
                    'ParentHostId': ParentHostId,
                    'BladeSlotList': FreeSlots,
                },
                })
        else:
            hh[line['fat_name']]['nodes'].append(line)
    for key in hh.keys():
        """занимаем только нужное количество слотов"""
        row = len(hh[key]['nodes'])
        empty = len(hh[key]['payload']['BladeSlotList'])
        arr = hh[key]['payload']['BladeSlotList']
        while empty > row:
            empty = empty - 1;arr.pop()
    return hh

def check_blade(auth, line):
    url = '{}/api/templates/host-blades?orgUnitId={}&dataCenterId={}&freeSlots=True&$filter=Name eq \'{}\''.format(
        auth.api_domain,
        line['OrgUnitId'],
        line['DataCenterId'],
        line['fat_name'],
        )
    r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)[0]
    return json_1['FreeSlots'],json_1['Id']

def to_plan_node(auth, read):
    reader = {
        'to work': read, # отфильтрованы только нужные
        'check': [], # на проверке
        'error': [], # какие-то ошибки
        'ok': [], # всё хорошо
    }
    hh = get_parent_for_nodes(auth, reader['to work'])
    for key in hh.keys():
        len_ = 0
        for line in hh[key]['nodes']:
            len_ = len_ + int(len(to_plan.check_host(auth, line['new_name'])))
        if len_ == 0:
            pprint('{} и {} хост(а) пошли'.format(
                key,
                len(hh[key]['nodes']),
                ))
            hh[key] = to_plan.create(auth, hh[key]['payload'], hh[key])
        else:
            line.update({'error': 'дубликат хоста'})
    print('присваиваем метки')
    for key in hh.keys():
        kick.set_sap_id(auth, hh[key]['nodes'])

    print('переименовываем серверы')
    for key in hh.keys():
        kick.rename_hosts(auth, hh[key]['nodes'])
    pprint(hh)

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
