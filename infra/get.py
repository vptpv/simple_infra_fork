import requests, json
from pprint import pprint
from infra import kick, metod
from sheets import write

def sap_4_node(auth):
    print('\tномер ряда')
    answer = input('\n\tответ: ').strip()
    data = int(answer) #номер ряда
    rackrow = f" and RackRow eq '{data}'"
    select = 'HostName,AccountingId,HardwareModelName,Rack'
    filter_ = f"HardwareSubTypeName eq '0U' and DataCenterLocationName eq 'ICVA'{rackrow}"
    url = f"{auth.api_domain}/api/hardware-items?$select={select}&$filter={filter_}"
    r = requests.get(url, cookies = auth.cookies)
    json_1 = json.loads(r.text)
    list_ = []
    list_ = [[['SAP ID','Left','Left_b','Right','Right_b']],[]]
    for x in json_1:
        if x.get('HostName') is not None:
            string = [
                x.get('AccountingId'),
                '',
                x.get('HardwareModelName')[3:],
                x.get('HostName'),
                ''
            ]
            list_[0].append(string)
            string = [
                f"{x.get('AccountingId')};;{x.get('HardwareModelName')[3:]};{x.get('HostName')};",
                x.get('Rack'),
                x.get('HostName')[-3:]
            ]
            list_[1].append(string)
    write.stickers_data(list_[0])
    write.temp(list_[1])
    print('готово')

def zip(auth):
    print('\nначинаю крутить-вертеть\n')
    select = 'HardwareTypeName,HardwareSubTypeName,HardwareModelName,HardwareModelId,SAPMaterialNumber,InstalledInto,DataCenterLocationName,DataCenterName'
    conditions = [
        "HostName eq null",
        " and IsActual eq true",
        " and IsInTransit eq false",
        " and IsRepairInProgress eq false",
        " and InstalledDate eq null",
        " and InstalledInto eq null"
    ]
    filter_ =''
    for x in conditions:
        filter_ = filter_ + x
    url = f"{auth.api_domain}/api/hardware-items?$select={select}&$filter={filter_}&$orderby=HardwareModelName asc"
    r = requests.get(url, cookies = auth.cookies)
    json_1 = json.loads(r.text)
    dict_ = {}                  # этап 1 считаем
    for x in json_1:                                    # суммируем уникальные ключи
        if x.get('InstalledInto') is None:              # которые никуда не установлены
            if dict_.get(json.dumps(x), 0) == 0:        # если ключ уникальный
                dict_.update([(json.dumps(x),1)])       # добавляем его в хеш со значением один
            else:                                       # иначе
                dict_[json.dumps(x)]+=1                 # увеличиваем значение ключа на еденицу
    list_ = []                  # этап 2 собираем
    for x in dict_.items():                             # перебераем получившиеся пары
        y = json.loads(x[0])                            # парсим хеш ключа
        y.update([('Quantity',x[1])])                   # и дописываем в него количество
        list_.append(y)                                 # получившееся дописываем в массив
    list_2 = []                 # этап 3 генерим данные для записи в таблицу
    for x in list_:
        sapMaterial = f"000{x.get('SAPMaterialNumber')}"
        sapMaterial = sapMaterial[-4:]
        y = [
            sapMaterial,str(x.get('HardwareModelId')),
            f"{x.get('HardwareTypeName')} {x.get('HardwareSubTypeName')}",
            x.get('HardwareModelName'),
            x.get('Quantity'),
            x.get('DataCenterLocationName'),
            x.get('DataCenterName')
        ]
        list_2.append(y)
    write.stock(list_2)
    print('данные об остатках записаны')
    drop_down_list(list_2)
    print('выпадающий список обновлён')
    hw_models(auth)
    print('выгрузили данные о моделях')
    zip_os(auth)
    print('выгрузили данные об ОС')
    print('\nконец')

def drop_down_list(list_2):
    dict_ = {}                  # этап 1 считаем
    for x in list_2:                            # 
        if dict_.get(x[3], 0) == 0:             # если ключ уникальный
            dict_.update([(x[3],x[4])])         # добавляем его в хеш со значением
        else:                                   # иначе
            dict_[x[3]] = dict_[x[3]] + x[4]    # увеличиваем значение ключа на еденицу

    list_ = []                  # этап 2 генерим данные для записи в таблицу
    for x in dict_.items():                     # перебераем получившиеся пары
        y = [x[0],x[1]]                         # получившееся дописываем в массив
        list_.append(y)                         # получившееся дописываем в массив

    write.accounting(list_, 1)

def zip_os(auth): #выгрузить список меток с моделями для VK
    conditions = {
        'select': [
            "IsActual",",",
            "HardwareAddresses",",",
            "AccountingId",",",
            "HostName",",",
            "SerialNumber",",",
            "HardwareModelName",",",
            "HardwareModelId",",",
            "HardwareConfigurationName",",",
            "IsInTransit",",",
            "DataCenterLocationName",",",
            "DataCenterName",",",
            "OrgUnitName",",",
            "HostLinkedDateTime",",",
            "WorkTask",",","Tasks"
        ],
        'filter': [
            "IsActual eq true and IsAsset eq true ", # основные средства
            "IsActual eq true and HardwareModelName eq 'DDR4 128GB Optane DC PM' and InstalledInto eq null and IsInTransit eq false", # оптаны
        ]
    }
    select =''
    for x in conditions['select']:
        select = select + x
    # filter_ =''
    list_2 = [[],[],[]]
    for x in conditions['filter']:
        filter_ = x
        url = f"{auth.api_domain}/api/hardware-items?$select={select}&$filter={filter_}&$orderby=DataCenterLocationName desc"
        r = requests.get(url, cookies = auth.cookies)
        json_1 = json.loads(r.text)
        list_ = []
        for x in json_1:
            list_.append(json.loads(json.dumps(x)))
        # list_2 = [[],[],[]]
        for x in list_:
            mac_address = x.get('HardwareAddresses')
            pur_task = [task for task in x.get('Tasks') if task[0:3].lower() == "pur"]
            wor_task = [x.get('WorkTask')]
            hot_task = [task for task in x.get('Tasks') if task.lower() == "vkeng-4274" or task.lower() == "vkeng-3623"]
            mega_string = f"{x.get('SerialNumber')} {x.get('DataCenterLocationName')} hot: {hot_task} work: {wor_task}"
            y = [
                x.get('AccountingId'),
                x.get('SerialNumber'),
                x.get('HardwareModelName'),
                pur_task[0] if len(pur_task) == 1 else '',
                mac_address[0] if len(mac_address) == 1 else len(mac_address) if len(mac_address) > 1 else '',
                x.get('HardwareConfigurationName'),
                f"{x.get('DataCenterLocationName')} {x.get('DataCenterName')}" if x.get('DataCenterName') else x.get('DataCenterLocationName'),
                x.get('OrgUnitName'),
                hot_task[0] if len(hot_task) == 1 and hot_task == wor_task else f"{x.get('HostName')} {hot_task[0]}" if len(hot_task) == 1 and x.get('HostName') else x.get('HostName') if x.get('HostName') else f"{wor_task[0]} {hot_task[0]}" if len(hot_task) == 1 else '',
                x.get('HostLinkedDateTime'),
                ]
            list_2[0].append(y) if x.get('HardwareModelName')[0:4] != "DDR4" else ''
            # список горячих ОС
            list_2[1].append(y) if len(hot_task) > 0 or x.get('HardwareModelName')[0:4] == "DDR4" else ''#; print(mega_string) if len(hot_task) > 0 else ''
            # список ОС на горячем складе
            '' if x.get('IsInTransit') or x.get('HostName') or x.get('AccountingId')[0].lower() != "s" or len(hot_task) > 0 else list_2[2].append(y) if x.get('DataCenterLocationName').lower() == "icva" else ''
    write.servers(list_2[0],0)
    write.servers(list_2[1],1)
    write.servers(list_2[2],2)

def hw_models(auth):
    list_2 = []
    # url = f"{auth.api_domain}/api/hardware-models?$expand=Type,SubType&$filter=IsActual eq true&$orderby=SAPMaterialNumber asc"
    url = f"{auth.api_domain}/api/hardware-models?$expand=Type,SubType&$orderby=SAPMaterialNumber desc"
    r = requests.get(url, cookies = auth.cookies)
    json_1 = json.loads(r.text)
    # pprint(json_1[0]['SubType'])
    # pprint(json_1[0]['Type'])
    for i in json_1:
        # print(i)
        string = [
            f"0000{i.get('SAPMaterialNumber')}"[-4:],
            i.get('Id'),
            f"{i.get('Type')['Name']} {i.get('SubType')['Name']}",
            i.get('Name')
        ]
        list_2.append(string)
    write.accounting(list_2,0)

def sap_from_param(auth, reader, param):
    for line in reader:
        params = {
            'name': ['HostName',metod.hostname(line['new_name'])],
            # 'serial': ['SerialNumber',line['serial']],
            'serial': ['SerialNumber',line.get('serial', 'none')],
            }
        url = f"{auth.api_domain}/api/hardware-items?$filter={params[param][0]} eq '{params[param][1]}'"
        r = requests.get(url, cookies = auth.cookies)
        json_1 = json.loads(r.text)
        try:
            sapId = str(json_1[0]["AccountingId"])
        except IndexError:
            print(f"{params[param][1]}\tне в стойке")
        except KeyError:
            pprint(json_1)
        else:
            print(f"{params[param][1]}\t{sapId}")

def sn_from_sap(auth, reader):
    for line in reader:
        data = {
                'sapid': f"$filter=AccountingId eq '{line['asset_tag']}'"
            }
        url = f"{auth.api_domain}/api/hardware-items?{data['sapid']}"
        r = requests.get(url, cookies = auth.cookies)
        json_1 = json.loads(r.text)
        try:
            serialNumber = str(json_1[0]["SerialNumber"])
        except IndexError:
            print(f"{line['asset_tag']} - нетю")
        else:
            print(f"{serialNumber}\t{line['asset_tag']}")

def vacant_sap_4_node(auth):
    HardwareModelId = {
    '4U_FatTwin_G2_Node': 6118,
    '4U_FatTwin_G3_Node': 6119
    }
    print('\tкакое поколение 2/3?')
    generation = int(input('\n\tответ: ').strip())
    if generation == 2:
        generation = '4U_FatTwin_G2_Node'
    elif generation == 3:
        generation = '4U_FatTwin_G3_Node'
    print(f"\tсколько меток {generation} нужно?")
    how_much = int(input('\n\tответ: ').strip())
    select = 'HostName,AccountingId,HardwareModelName,Rack'
    conditions = [
        f"HardwareModelId eq {HardwareModelId[generation]}",
        " and DataCenterLocationName eq 'ICVA Stock'",
        " and SerialNumber eq null",
        " and IsActual eq true",
        " and IsInTransit eq false",
        " and HardwareConfigurationId eq null"
    ]
    filter_ =''
    for x in conditions:
        filter_ = filter_ + x
    url = f"{auth.api_domain}/api/hardware-items?$top={how_much}&$select={select}&$filter={filter_}"
    print(url)
    r = requests.get(url, cookies = auth.cookies)
    json_1 = json.loads(r.text)
    list_ = [[['SAP ID','Left','Left_b','Right','Right_b']],[]]
    for x in json_1:
        if x.get('HostName') is None:
            sticker = [
                x.get('AccountingId'),
                '',
                x.get('HardwareModelName')[3:],
                '',
                ''
            ]
            serial_number = {'asset_tag':x.get('AccountingId'),'serial':x.get('AccountingId')}
            list_[0].append(sticker)
            list_[1].append(serial_number)
    write.stickers_data(list_[0])
    answer = input('\nзастолбить метки?\t\nответ: ').strip()
    if answer == 'да':
        kick.add_sn(auth, list_[1])
    print('готово')
