import requests, json
from pprint import pprint

# возможно, скоро пригодится
def node_rename(reader):
    for line in reader:
        hostname_x = hostname(line['name'].strip())
        temp_x = nb.dcim.devices.get(name=hostname_x)
        if temp_x is None:
            print(f"{hostname_x}\tне найден")
        else:
            f_unit = first_unit(temp_x.parent_device.name)
            node = int(temp_x.parent_device.device_bay.name[-1])
            hostname_y = f"{hostname_x[0:3]}{temp_x.parent_device.name[-6:-3]}{str(int(temp_x.parent_device.name[-3:])-f_unit+(node-1))}"
            # print(hostname_y)
            comment = line['comments'].strip() + ' // ' +temp_x.comments
            temp_y = nb.dcim.devices.get(name=hostname_y)
            if temp_y is None:
                temp_x.update({
                    'name': hostname_y,
                    'comments': comment
                })
                print(f"{hostname_x}\t{hostname_y}\t{temp_x.parent_device.name}")
            else:
                print(f"{hostname_x}\t{hostname_y}\tуже существует")

def set_task_hosts(reader):
    for line in reader:
        url = f"{api_domain}/api/hosts?$filter=HostName eq '{line['old_name']}'"
        r = requests.get(url, cookies=get_cookie())
        json_1 = json.loads(r.text)
        try:
            hostId = str(json_1[0]["Id"])
            hostName = str(json_1[0]["HostName"])
        except IndexError:
            print(f"{line['old_name']} - не в стойке")
        else:
            if line['task'] != '':
                set_task(hostId, line['task'])
            print(f"{line['old_name']}\t{line['task']}")

def set_task(cookie, hostId, task):
    url = f"{api_domain}/api/hosts/{hostId}/update-task-requests"
    payload = {
        "Task": task
        # "TaskName": task
    }
    r = requests.post(url, cookies=cookie, data=json.dumps(payload), headers=headers)
    print(r.status_code)
    if r.status_code == 200:
        print('что-то получилось')

# совсем не то что было нужно
def set_org_unit_name(cookie, reader):
    url = f"{api_domain}/api/hosts/org-unit/batch-change"
    payload = [{
        "HostNames": [],
        # "HostName": line['old_name'],
        "OrgUnitName": "UMAgency",
        "Task": "VKENG-2964"
    }]
    for line in reader:
        payload[0]["HostNames"].append(line['new_name'])
    # pprint(payload)
    r = requests.post(url, cookies=cookie, data=json.dumps(payload[0]), headers=headers)
    if r.status_code == 200:
        print(f"вроде присвоились")
    else:
        print(r.status_code)

# тестовая выгрузка зипа
def get_zip_2(auth):
        print('\nначинаю крутить-вертеть\n')
        select = [
            'HardwareTypeName,',
            'HardwareSubTypeName,',
            'HardwareModelName,',
            'HardwareModelId,',
            'SAPMaterialNumber,',
            'DataCenterLocationName,',
            'DataCenterName,',
            'OrgUnitId',
        ]
        select_ =''
        for x in select:
            select_ = select_ + x
        conditions = [
            'HostName eq null',
            ' and HardwareModelId eq 469',
            ' and IsActual eq true',
            ' and IsInTransit eq false',
            ' and IsRepairInProgress eq false',
            ' and InstalledInto eq null',
        ]
        filter_ =''
        for x in conditions:
            filter_ = filter_ + x
        url = f"{auth.api_domain}/api/hardware-items?$select={select_}&$filter={filter_}&$orderby=HardwareModelName asc"
        print(url)
        r = requests.get(url, cookies = auth.cookies)
        json_1 = json.loads(r.text)
        dict_ = {}                  # этап 1 считаем
        for x in json_1:                                    # суммируем уникальные ключи
            if x.get('OrgUnitId') != 198:                   # игнорируем офис
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
        pprint(list_2)
