import requests, json, time, sys
from pprint import pprint
from infra import metod, kick
from sheets import read, write

def get_hwmodelid():
    # по хорошему стоит проверять ноды на складе но пока так
    return 6119

def get_ip_address(CustomHostName):
    # чекаем список адресов от админа на листе temp
    arr = read.smart('accounting',4)
    if len(arr) > 0:
        hh = {}
        for line in arr:
            hh.update({line[0].lower():line[1]})
        string = hh.get(CustomHostName.lower(),'0.0.0.0')
    else:
        string = '0.0.0.0'
    return string

def get_data_from_host(auth, hostname, payload):
    loca,group,row,rack = metod.get_location(hostname, payload.get('TemplateName'))
    # получаем номер локации:
    url = "{}/api/data-center-locations?$filter=Name eq '{}'".format(
        auth.api_domain,
        loca, # нужно получить из имени
        )
    r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
                                                                                    # номер локации
    DataCenterLocationId = json_1[0].get('Id', 'хуй')
    payload.update({'DataCenterLocationId': DataCenterLocationId})
    # получаем номер нужного цода в локации:
    url = "{}/api/data-center-locations/{}/data-centers?$filter=Name eq '{}'".format(
        auth.api_domain,
        payload.get('DataCenterLocationId'),
        group, # нужно получить из имени
        )
    r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
                                                                                    # номер цода
    DataCenterId = json_1[0].get('Id', 'хуй')
    payload.update({'DataCenterId': DataCenterId})
    # получаем номер ряда
    url = "{}/api/data-centers/{}/rows?$filter=Name eq '{}'".format(
        auth.api_domain,
        DataCenterId,
        row, # нужно получить из имени
        )
    # print(url)
    r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
                                                                                    # номер ряда
    DataCenterRowId = json_1[0].get('Id', 'хуй')
    payload.update({'DataCenterRowId': DataCenterRowId})
                                                                                    # получаем номер и юнит стойки
    url = "{}/api/data-centers/rows/{}/racks?$filter=Name eq '{}'".format(
        auth.api_domain,
        DataCenterRowId,
        rack, # нужно получить из имени
        )
    r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
                                                                                    # номер стойки
    DataCenterRackId = json_1[0].get('Id', 'хуй')
    payload.update({'DataCenterRackId': DataCenterRackId})
                                                                                    # номер оргЮнита
    OrgUnitId = json_1[0].get('OrgUnits', 'хуй')[0]
    payload.update({'OrgUnitId': OrgUnitId})
    return payload,group

def get_data_from_id(auth, asset_tag, payload):
    sap_id = check_id(auth, asset_tag)
                                                                                    # тип хоста
    payload.update({'TemplateName': sap_id['HardwareTypeName']})
                                                                                    # номер модели
    payload.update({'HardwareModelId': sap_id['HardwareModelId']})
                                                                                    # номер юрика
    payload.update({'BalanceUnitId': int(sap_id['BalanceUnitId'])})
    if payload.get('TemplateName') == 'Network':
                                                                                    # тип устройства
        payload.update({'NetworkType': sap_id['HardwareSubTypeName']})
                                                                                    # ip address
        payload.update({'Ip':get_ip_address(payload.get('CustomHostName'))})
        if payload.get('NetworkType') == 'Switch':
                                                                                    # роль свича
            payload.update({'NetworkRoles': get_role(auth, sap_id['HardwareModelName'])})
    if payload.get('TemplateName') == 'Blade':
                                                                                    # молель нод
        payload.update({'BladeServerHardwareModelId': get_hwmodelid()})
    if payload.get('TemplateName') == 'Server':
                                                                                    # количество серверов
        payload.update({'HostQuantity': 1})
    return payload,sap_id

def check_id(auth, asset_tag):
    url = "{}/api/hardware-items?$filter=AccountingId eq '{}'".format(
        auth.api_domain,
        asset_tag
        )
    r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
    return json_1[0]

def check_host(auth, hostname):
    url = "{}/api/hosts?$filter=HostName eq '{}'".format(
        auth.api_domain,
        hostname
        )
    r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
    return json_1

def get_role(auth, name):
    url = "{}/api/hardware-models?$top=1&$expand=Attributes&$filter=Name eq '{}'".format(
        auth.api_domain,
        name
        )
    r = requests.get(url, cookies = auth.cookies);json_1 = json.loads(r.text)
    for i in json_1[0]['Attributes']:
        if i.get('Name', 'хуй') == 'Network Roles':
            return [i.get('TextValue').split(',')[0].strip()]

# тут собирается запрос
def make_payload(auth, line):
    payload = {}
    payload.update({'InstallationTask': line.get('task', '')})
    payload.update({'CustomHostName': line.get('new_name', '')})
    if line['asset_tag'] == '':
        line.update({'error': 'нет метки'})
        return payload,line
    else:
        payload,sap_id = get_data_from_id(auth, line['asset_tag'], payload)
    location = sap_id['DataCenterLocationName']
    if line['new_name'] != '' and location == 'ICVA':
        payload,group = get_data_from_host(auth, line['new_name'], payload)
        try:
            unit = int(line.get('unit', '').split(' ')[0])
        except ValueError:
            line.update({'unit': ''})
        else:
            line.update({'unit': unit})
        if line.get('unit', '') == '' and payload.get('TemplateName') == 'Server':
            line.update({'unit': metod.position(line['new_name'], group)})
            payload.update({'FirstUnit': line['unit']})
        elif type(line['unit']) is int:
            payload.update({'FirstUnit': line['unit']})
    elif line['new_name'] == '':
        line.update({'error': 'нет имени хоста'})
    else:
        line.update({'error': 'железка где-то не там: {}'.format(location)})
    return payload,line

# тут запрос отправляется
def create(auth, payload, line):
    url = '{}/api/hosts'.format(auth.api_domain)
    r = requests.post(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
    line.update({'status_code': r.status_code})
    if r.status_code == 200:
        if payload.get('BladeSlotList', 0) != 0:
            """если нода, записываем имя и статус в каждый хост"""
            message = json.loads(r.text)
            i = 0
            for each in message:
                line['nodes'][i].update({'old_name': each['Name']})
                line['nodes'][i].update({'status_code': r.status_code})
                i += 1
        else:
            old_name = json.loads(r.text)[0]['Name']
            line.update({'old_name': old_name})
    else:
        error = json.loads(r.text)['Message']
        line.update({'error': [error, payload]})
    return line

def test(auth, read):
    reader = {
        'to work': read, # отфильтрованы только нужные
        'check': [], # на проверке
        'error': [], # какие-то ошибки
        'ok': [], # всё хорошо
    }
    # print(reader['to work'])
    for line in reader['to work']:
        payload,line = make_payload(auth, line)
        print(line);pprint(payload)
        if line.get('error', 0) != 0:
            reader['error'].append(line)
        elif len(check_host(auth, line['new_name'])) == 0:
            print('запрос', end=' ')
            tic = time.perf_counter()
            reader['check'].append(create(auth, payload, line))
            toc = time.perf_counter()
            print('&.2f' & toc-tic)
        else:
            line.update({'error': 'уже есть'})
            reader['error'].append(line)
    # проверяем ответы сервера
    print('\nпроверяем ответы')
    for line in reader['check']:
        if line.get('error', 0) != 0:
            reader['error'].append(line)
            # print('{}\t{}'.format(line['new_name'],line['old_name']))
        elif line.get('old_name', 0) != 0:
            reader['ok'].append(line)
            # print('{}\t{}'.format(line['new_name'],line['error']))
    pprint(reader['error'])
    # pprint(reader['ok'])

    print('\tприсваиваем метки')
    kick.set_sap_id(auth, reader['ok'])
    # print('начинаем обратный отсчёт')
    # for i in range(300,0,-1):
    #     sys.stdout.write(str(i)+' ')
    #     sys.stdout.flush()
    #     time.sleep(1)
    print('переименовываем серверы')
    # kick.rename_sap(auth, reader['ok'])
    kick.rename_hosts(auth, reader['ok'])
