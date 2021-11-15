import requests, json
from pprint import pprint
from infra import metod, kick
from sheets import write

def get_hwmodelid():
    # по хорошему стоит проверять ноды на складе но пока так
    return 6119

def get_ip_address():
    # нужно как-то научиться чекать свободные адреса
    string = '192.168.0.0'
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
    payload                                                                                     
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
                                                                                    # где лежит
    payload.update({'DataCenterLocationId_fuck': sap_id['DataCenterLocationId']})
    if payload.get('TemplateName') == 'Network':
                                                                                    # тип устройства
        payload.update({'NetworkType': sap_id['HardwareSubTypeName']})
                                                                                    # ip address
        payload.update({'Ip':get_ip_address()})
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
        print('нет метки');exit()
    else:
        payload,sap_id = get_data_from_id(auth, line['asset_tag'], payload)
    location = sap_id['DataCenterLocationName']
    if line['new_name'] != '' and location == 'ICVA':
        payload,group = get_data_from_host(auth, line['new_name'], payload)
        if line.get('unit', '') == '' and payload.get('TemplateName') != 'Network':
            payload.update({'FirstUnit': metod.position(line['new_name'], group)})
    elif line['new_name'] == '':
        print('нет имени хоста\n\t{}'.format(line['asset_tag']));payload.clear()
    else:
        print('железка где-то не там:\n\t{} {}'.format(line['asset_tag'],location));payload.clear()
    pprint(payload)

# тут запрос отправляется
def create(auth, payload, line):
    url = '{}/api/hosts'.format(auth.api_domain)
    r = requests.post(url, cookies = auth.cookies, data=json.dumps(payload), headers = auth.headers)
    line.update({'status_code': r.status_code})
    if r.status_code == 200:
        old_name = json.loads(r.text)[0]['Name']
        line.update({'old_name': old_name})
    else:
        error = json.loads(r.text)['Message']
        line.update({'error': [error, payload]})
    return line

def test(auth, reader):
    reader_2 = []
    reader_3 = []
    for line in reader:
        if line[':-)'] == 'TRUE':
            reader_2.append(line)
    print(reader_2)
    for line in reader_2:
        if len(check_host(auth, line['new_name'])) == 0:
            reader_3.append(create(auth, make_payload(auth, line), line))
        else:
            line.update({'error': 'уже есть'})
            reader_3.append(line)
    for line in reader_3:
        if line.get('error', '') == '':
            print('{}\t{}'.format(line['new_name'],line['old_name']))
        else:
            print('{}\t{}'.format(line['new_name'],line['error']))
