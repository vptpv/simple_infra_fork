import json
import time
import os
import requests
from keepass_db import KeePassDB
from pprint import pprint
import utils


class Infra:
    def __init__(self, config, sheet=None, jira=None):  # получаем печеньки из файла
        self.api_domain = config['cmdb']['api_domain']
        self.standby = config['cmdb']['standby']
        self.sheet = sheet
        self.jira = jira
        self.my_base = ''
        if os.path.exists('temp/api_domain') is False:
            if self.my_base == '':
                self.my_base = KeePassDB(config)
            self.api_domain = self.my_base.entry.notes
            file = open('temp/api_domain', 'w')
            file.write(self.api_domain)
            file.close()
        else:
            file = open('temp/api_domain', 'r')
            self.api_domain = file.read()
            file.close()
            if len(self.api_domain) != 23:
                if self.my_base == '':
                    self.my_base = KeePassDB(config)
                self.api_domain = self.my_base.entry.notes
                file = open('temp/api_domain', 'w')
                file.write(self.api_domain)
                file.close()
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        if os.path.exists('temp/cookies.json') is False:
            self.user_data = ''
            self.cookies = {"Name": "Value"}
        else:
            file = open('temp/cookies.json', 'r')
            self.user_data = json.loads(file.read())
            file.close()
            self.cookies = {self.user_data.get('Name', 'huy'): self.user_data.get('Value', 'huy')}
        if os.path.exists('temp/credentials.json') is False:
            if self.my_base == '':
                self.my_base = KeePassDB(config)
            data_ta = str(self.my_base.credentials)
            data_ta = data_ta[2:-1].split('\\n')
            file = open('temp/credentials.json', 'w')
            for i in data_ta:
                file.write(i + '\n')
            file.close()
        if os.path.exists('temp/jira_bot.json') is False:
            if self.my_base == '':
                self.my_base = KeePassDB(config)
            data_ta = str(self.my_base.jira_bot)
            data_ta = data_ta[2:-1].split('\\n')
            file = open('temp/jira_bot.json', 'w')
            for i in data_ta:
                file.write(i + '\n')
            file.close()

    def _request(self, method, url):
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        req = requests.request(method, self.api_domain + url, headers=headers, cookies=self.cookies)
        if req.status_code != 503:
            return req
        else:
            return requests.request(method, self.standby + url)

    def make_get(self, url):
        return self._request('GET', url)

    def make_post(self, url):
        return self._request('POST', url)

    def make_put(self, url):
        return self._request('PUT', url)

    def make_delete(self, url):
        return self._request('DELETE', url)

    def test(self):
        return self.sheet.read_another()

    def check_access(self):
        url = f"{self.api_domain}/api/hosts?$filter=DataCenterRackName eq '604'&$top=1"
        r = requests.get(url, cookies=self.cookies)
        # print(r.status_code)
        return r.status_code

    def new_check_access(self):
        url = f"/api/hosts?$filter=DataCenterRackName eq '604'&$top=1"
        r = self.make_get(url)
        # print(r.status_code)
        return r.status_code

    def get_new_cookies(self, kp_base):
        self.my_base = kp_base
        status_code = 1
        url = f"{self.api_domain}/api/login"
        while status_code != 200:
            payload = self.my_base.make_payload()
            r = requests.post(url, data=json.dumps(payload), headers=self.headers)
            self.user_data = json.loads(r.text)
            self.user_data.update([("UserName", payload.get('Name'))])
            if self.user_data.get('Name', 'хуй') != 'хуй':
                self.cookies = {self.user_data.get('Name'): self.user_data.get('Value')}
            file = open('temp/cookies.json', 'w')
            file.write(json.dumps(self.user_data))
            file.close()
            status_code = r.status_code
            if status_code != 200:
                print(r.status_code, r.text)
        print('свежие куки получены')

    def get_zip(self):
        print('\nначинаю крутить-вертеть\n')
        select = [
            'HardwareTypeName',
            'HardwareSubTypeName',
            'HardwareModelName',
            'HardwareModelId',
            'SAPMaterialNumber',
            'DataCenterLocationName',
            'DataCenterName',
            'OrgUnitId',
        ]
        select_ = ', '.join(select)
        conditions = [
            'HostName eq null',
            ' and IsActual eq true',
            ' and IsInTransit eq false',
            ' and IsRepairInProgress eq false',
            ' and InstalledInto eq null',
        ]
        filter_ = " ".join(conditions)

        url = f"/api/hardware-items?$select={select_}&$filter={filter_}&$orderby=HardwareModelName asc"
        r = self.make_get(url)
        json_1 = json.loads(r.text)
        dict_ = {}  # этап 1 считаем
        for x in json_1:  # суммируем уникальные ключи
            if x.get('OrgUnitId') != 198:  # игнорируем офис
                if dict_.get(json.dumps(x), 0) == 0:  # если ключ уникальный
                    dict_.update([(json.dumps(x), 1)])  # добавляем его в хеш со значением один
                else:  # иначе
                    dict_[json.dumps(x)] += 1  # увеличиваем значение ключа на единицу
        list_ = []  # этап 2 собираем
        for x in dict_.items():  # перебираем получившиеся пары
            y = json.loads(x[0])  # парсим хеш ключа
            y.update([('Quantity', x[1])])  # и дописываем в него количество
            list_.append(y)  # получившееся дописываем в массив
        list_2 = []  # этап 3 генерим данные для записи в таблицу
        for x in list_:
            sap_material = str(x.get('SAPMaterialNumber')).zfill(4)
            y = [
                sap_material,
                str(x.get('HardwareModelId')),
                f"{x.get('HardwareTypeName')} {x.get('HardwareSubTypeName')}",
                x.get('HardwareModelName'),
                x.get('Quantity'),
                x.get('DataCenterLocationName'),
                x.get('DataCenterName')
            ]
            list_2.append(y)
        print('данные об остатках', end='')
        self.sheet.stock(list_2)
        print(' записаны')
        print('выпадающий список', end='')
        self.drop_down_list(list_2)
        print(' обновлён')
        print('данные о моделях', end='')
        self.hw_models()
        print(' выгрузили')
        print('данные об ОС:', end='\n')
        self.zip_os()
        print(' выгрузили')
        print('\nконец')

    def drop_down_list(self, list_2):
        dict_ = {}  # этап 1 считаем
        for x in list_2:  #
            if x[3] in dict_:  # если ключ уже есть
                dict_[x[3]] += x[4]  # увеличиваем значение ключа
            else:  # иначе
                dict_[x[3]] = x[4]  # добавляем его в хеш со значением

        list_ = list(dict_.items())  # этап 2 генерим данные для записи в таблицу
        self.sheet.accounting(list_, 1)

    def zip_os(self):  # выгрузить список меток с моделями для VK
        if not self.jira:
            print("zip_os require Jira initialization")
            exit(1)
        hot_tasks = self.jira.hot_zip()
        ne_huist = self.sheet.read_another()
        conditions = {
            'select': [
                "IsActual", ",",
                "HardwareAddresses", ",",
                "AccountingId", ",",
                "HostName", ",",
                "SerialNumber", ",",
                "HardwareModelName", ",",
                "HardwareModelId", ",", "HardwareTypeName", ",",
                "HardwareConfigurationName", ",",
                "HardwareOriginalModelName", ",",
                "IsInTransit", ",",
                "DataCenterLocationName", ",",
                "DataCenterName", ",",
                "OrgUnitName", ",",
                "HostLinkedDateTime", ",",
                "WorkTask", ",", "Tasks"
            ],
            'filter': [
                "IsActual eq true and IsAsset eq true ",  # основные средства
                "IsActual eq true and HardwareModelName eq 'DDR4 128GB Optane DC PM' "
                "and InstalledInto eq null and IsInTransit eq false",  # оптаны
            ]
        }
        select = ''
        for x in conditions['select']:
            select = select + x
        list_hw_models = []
        list_2 = [[], [], [], {'accounting': [], 'servers': []}]  # 0  1  2  3
        for filter_ in conditions['filter']:
            url = f"{self.api_domain}/api/hardware-items?$select={select}&$filter={filter_}" \
                  f"&$orderby=DataCenterLocationName desc"
            r = requests.get(url, cookies=self.cookies)
            json_1 = json.loads(r.text)
            list_ = []
            for x in json_1:
                list_.append(json.loads(json.dumps(x)))
            for x in list_:
                mac_address = x.get('HardwareAddresses')
                pur_task = [task for task in x.get('Tasks') if task[0:3].lower() == "pur"]
                wor_task = [x.get('WorkTask')]
                hot_task = []
                for task_ in hot_tasks:
                    ksat = [task for task in x.get('Tasks') if task.lower() == task_.lower()]
                    hot_task.append(ksat[0]) if len(ksat) == 1 else ''
                mega_string = f"{x.get('SerialNumber')} {x.get('DataCenterLocationName')} " \
                              f"hot: {hot_task} work: {wor_task}"
                if x.get('DataCenterName'):
                    dc_line = f"{x.get('DataCenterLocationName')} {x.get('DataCenterName')}"
                else:
                    dc_line = f"{x.get('DataCenterLocationName')}"
                y = [
                    x.get('AccountingId'),
                    x.get('SerialNumber'),
                    x.get('HardwareModelName'),
                    x.get('HardwareOriginalModelName'),
                    pur_task[0] if len(pur_task) == 1 else '',
                    mac_address[0] if len(mac_address) == 1 else len(mac_address) if len(mac_address) > 1 else '',
                    x.get('HardwareConfigurationName'),
                    dc_line,
                    x.get('OrgUnitName'),
                    # если есть только хот_таск
                    # если есть хост и хот_таск
                    # если есть только хост
                    str(hot_task) if len(hot_task) > 0 else f"{x.get('HostName')} {str(hot_task)}" if x.get(
                        'HostName') and len(hot_task) > 0 else x.get('HostName') if x.get('HostName') else '',
                    x.get('HostLinkedDateTime'),
                ]
                # список серверов с именами моделей
                hw_model = [y[9], y[0], y[2], y[1], x.get('HardwareOriginalModelName')]
                list_hw_models.append(hw_model) if x.get('HardwareTypeName') == "Server" else ''
                # список ОС с именами моделей
                list_2[0].append(y) if x.get('HardwareModelName')[0:4] != "DDR4" else ''
                # список горячих ОС
                list_2[1].append(y) if len(hot_task) > 0 or x.get('HardwareModelName')[
                                                            0:4] == "DDR4" else ''  # ; print(mega_string) if len(hot_task) > 0 else ''
                # список ОС на горячем складе
                '' if x.get('IsInTransit') or x.get('HostName') or x.get('AccountingId')[0].lower() != "s" or len(
                    hot_task) > 0 else list_2[2].append(y) if x.get('DataCenterLocationName').lower() == "icva" else ''
                # список ОС проекты
                if len(pur_task) == 1 and ne_huist.get(pur_task[0], 'хуй') != 'хуй':
                    huist = [ne_huist.get(y[4]), y[0], y[4], y[7], y[8], y[9]]
                    #         #0                  1    2    3    4    5
                    list_2[3]['servers'].append(huist)
                    list_2[3]['accounting'].append([huist[1], huist[0]])
                # list_2[3]['servers'].append(huist);list_2[3]['accounting'].append([huist[1],huist[0]]) if len(pur_task) == 1 and ne_huist.get(pur_task[0], 'хуй') != 'хуй' else ''
        print('    список серверов с именами моделей', end='')
        self.sheet.hw_models(list_hw_models, 0)
        print(' <---эрон дон доне')
        print('    список ОС с именами моделей', end='')
        self.sheet.servers(list_2[0], 0)
        print(' <---эрон дон доне')
        print('    список горячих ОС', end='')
        self.sheet.servers(list_2[1], 1)
        print(' <---эрон дон доне')
        print('    список ОС на горячем складе', end='')
        self.sheet.servers(list_2[2], 2)
        print(' <---эрон дон доне')
        print('    список ОС проекты', end='')
        self.sheet.write_another(list_2[3])

    def hw_models(self):
        list_2 = []
        url = f"{self.api_domain}/api/hardware-models?$expand=Type,SubType&$orderby=SAPMaterialNumber desc"
        r = requests.get(url, cookies=self.cookies)
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
        self.sheet.accounting(list_2, 0)

    def sap_from_param(self, reader, param):
        for line in reader:
            params = {
                'name': ['HostName', utils.hostname(line['new_name'])],
                # 'serial': ['SerialNumber',line['serial']],
                'serial': ['SerialNumber', line.get('serial', 'none')],
            }
            url = f"{self.api_domain}/api/hardware-items?$filter={params[param][0]} eq '{params[param][1]}'"
            r = requests.get(url, cookies=self.cookies)
            json_1 = json.loads(r.text)
            try:
                sap_id = str(json_1[0]["AccountingId"])
            except IndexError:
                print(f"{params[param][1]}\tне в стойке")
            except KeyError:
                pprint(json_1)
            else:
                print(f"{params[param][1]}\t{sap_id}")

    def sap_4_node(self):
        print('\tномер ряда')
        answer = input('\n\tответ: ').strip()
        data = int(answer)  # номер ряда
        rackrow = f" and RackRow eq '{data}'"
        select = 'HostName,AccountingId,HardwareModelName,Rack'
        filter_ = f"HardwareSubTypeName eq '0U' and DataCenterLocationName eq 'ICVA'{rackrow}"
        url = f"{self.api_domain}/api/hardware-items?$select={select}&$filter={filter_}"
        r = requests.get(url, cookies=self.cookies)
        json_1 = json.loads(r.text)
        list_ = []
        list_ = [[['SAP ID', 'Left', 'Left_b', 'Right', 'Right_b']], []]
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
        self.sheet.stickers_data(list_[0])
        self.sheet.temp(list_[1])
        print('готово')

    def sn_from_sap(self, reader):
        for line in reader:
            data = {
                'sapid': f"$filter=AccountingId eq '{line['asset_tag']}'"
            }
            url = f"{self.api_domain}/api/hardware-items?{data['sapid']}"
            r = requests.get(url, cookies=self.cookies)
            json_1 = json.loads(r.text)
            try:
                serial_number = str(json_1[0]["SerialNumber"])
            except IndexError:
                print(f"{line['asset_tag']} - нетю")
            else:
                print(f"{serial_number}\t{line['asset_tag']}")

    def host_from_sap(self, reader):
        for line in reader:
            data = {
                'sapid': f"$filter=AccountingId eq '{line['asset_tag']}'"
            }
            url = f"{self.api_domain}/api/hardware-items?{data['sapid']}"
            r = requests.get(url, cookies=self.cookies)
            json_1 = json.loads(r.text)
            print(str(json_1[0].get("HostName", "хуй")) + f"\t{line['asset_tag']}")

    def vacant_sap_4_node(self):
        hardware_model_id = {
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
            f"HardwareModelId eq {hardware_model_id[generation]}",
            " and DataCenterLocationName eq 'ICVA Stock'",
            " and SerialNumber eq null",
            " and IsActual eq true",
            " and IsInTransit eq false",
            " and HardwareConfigurationId eq null"
        ]
        filter_ = ''
        for x in conditions:
            filter_ = filter_ + x
        url = f"{self.api_domain}/api/hardware-items?$top={how_much}&$select={select}&$filter={filter_}"
        print(url)
        r = requests.get(url, cookies=self.cookies)
        json_1 = json.loads(r.text)
        list_ = [[['SAP ID', 'Left', 'Left_b', 'Right', 'Right_b']], []]
        for x in json_1:
            if x.get('HostName') is None:
                sticker = [
                    x.get('AccountingId'),
                    '',
                    x.get('HardwareModelName')[3:],
                    '',
                    ''
                ]
                serial_number = {'asset_tag': x.get('AccountingId'), 'serial': x.get('AccountingId')}
                list_[0].append(sticker)
                list_[1].append(serial_number)
        self.sheet.stickers_data(list_[0])
        answer = input('\nзастолбить метки?\t\nответ: ').strip()
        if answer == 'да':
            self.add_sn(list_[1])
        print('готово')

    def rename_hosts(self, reader):
        for line in reader:
            url = f"{self.api_domain}/api/hosts?$filter=HostName eq '{line['old_name']}'"
            if line.get('status_code', 0) != 0:
                """если есть статус, значит работал скрипт и нужно ждать пока хост появится"""
                json_1 = []
                tic = time.perf_counter()
                while len(json_1) == 0:
                    r = requests.get(url, cookies=self.cookies)
                    json_1 = json.loads(r.text)
                    time.sleep(5)
                toc = time.perf_counter()
                print(str(toc - tic))

                url = f"{self.api_domain}/api/hosts/{line['old_name']}/name/{line['new_name']}"
                payload = {"Task": line['task']}
                r = requests.put(url, cookies=self.cookies, data=json.dumps(payload))
                print(r)
            else:
                r = requests.get(url, cookies=self.cookies)
                json_1 = json.loads(r.text)
                try:
                    host_id = str(json_1[0]["Id"])
                    host_name = str(json_1[0]["HostName"])
                except IndexError:
                    print(f"{line['old_name']} - не в стойке")
                else:
                    url = f"{self.api_domain}/api/hosts/{line['old_name']}/name/{line['new_name']}"
                    payload = {"Task": line['task']}
                    r = requests.put(url, cookies=self.cookies, data=json.dumps(payload))
                    print(f"{line['old_name']}\t{line['new_name']}\t{line['task']}")

    def rename_sap(self, reader):
        for line in reader:
            url = f"{self.api_domain}/api/hosts?$filter=SapInventory eq '{line['asset_tag']}'"
            r = requests.get(url, cookies=self.cookies)
            json_1 = json.loads(r.text)
            try:
                host_id = str(json_1[0]["Id"])
                host_name = str(json_1[0]["HostName"])
            except IndexError:
                print(f"{line['asset_tag']} - не в стойке")
            else:
                url = f"{self.api_domain}/api/hosts/{host_name}/name/{line['new_name']}"
                payload = {"Task": line['task']}
                r = requests.put(url, cookies=self.cookies, data=json.dumps(payload))
                print(f"{host_name}\t{line['new_name']}\t{line['task']}")

    def set_sap_id(self, reader):
        url = f"{self.api_domain}/api/hosts/accounting/batch-change"
        payload = []
        for line in reader:
            if line.get('status_code', 0) != 0:
                """если есть статус, значит работал скрипт и нужное имя в другом ключе"""
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
        r = requests.post(url, cookies=self.cookies, data=json.dumps(payload), headers=self.headers)
        if r.status_code == 200:
            print(f"вроде присвоились")
        else:
            print(f"{r.status_code}\t'{json.loads(r.text)['Message']}'")

    def add_sn(self, reader):  # вроде робит
        errors = []
        for line in reader:
            data = {
                'sapid': f"$filter=AccountingId eq '{line['asset_tag']}'",
                'serial': f"$filter=SerialNumber eq '{line['serial']}'"
            }
            url = f"{self.api_domain}/api/hardware-items?"
            r_ser = requests.get(url + data['serial'], cookies=self.cookies)
            json_ser = json.loads(r_ser.text)
            try:
                # hostId = str(json_1[0]["Id"])
                accounting_id = str(json_ser[0].get('AccountingId', 'хуй'))
            except KeyError:
                print(f"\n{line['asset_tag']}\t{line['serial']}\tчто блядь?")
                string = [line['asset_tag'], line['serial'], 'что блядь?']
                errors.append(string)
            except IndexError:
                r_sap = requests.get(url + data['sapid'], cookies=self.cookies)
                json_sap = json.loads(r_sap.text)
                try:
                    serial_number = str(json_sap[0]['SerialNumber'])
                except IndexError:
                    print(f"\n{line['asset_tag']}\t\tотсутствует железка")
                    string = [line['asset_tag'], line['serial'], 'отсутствует железка']
                    errors.append(string)
                else:
                    if json_sap[0].get('SerialNumber', '0') is None:
                        url = f"{self.api_domain}/api/accountings/{line['asset_tag'].upper()}/serial/{line['serial'].upper()}"
                        r = requests.put(url, cookies=self.cookies)
                        if r.status_code == 200:
                            print('^', end='')
                            # print(f"\n{str(json_sap[0]['AccountingId'])}\t{line['serial']}\tстало хорошо")
                            strong = f"{str(json_sap[0]['AccountingId'])}\t{line['serial']}\tстало хорошо"
                        else:
                            print(f"\n{line['asset_tag']}\t\tне дружелюбный ответ")
                            string = [line['asset_tag'], line['serial'], 'не дружелюбный ответ']
                            errors.append(string)
                    else:
                        print(
                            f"\n{line['asset_tag']}\t->{str(json_sap[0]['SerialNumber'])}<-\t{line['serial']}\tуже есть другой серийник")
                        string = [line['asset_tag'], line['serial'], str(json_sap[0]['SerialNumber'])]
                        errors.append(string)
                    # жуткий костыль
                    # elif json_sap[0].get('SerialNumber', '0') == 'AC1F6B92B535' and json_sap[0].get('AccountingId', '0') == 'SRV358743':
                    #     url = f"{auth.api_domain}/api/accountings/{line['asset_tag'].upper()}/serial/{line['serial'].upper()}"
                    #     r = requests.put(url, cookies = auth.cookies)
                    #     if r.status_code == 200:
                    #         print(f"{str(json_sap[0]['AccountingId'])}\t{line['serial']}\tстало хорошо")
            else:
                if accounting_id == line['asset_tag'].upper():
                    print('.', end='')
                    # print(f"{AccountingId}\t{str(json_ser[0]['SerialNumber'])}\tбыло хорошо")
                    strong = f"{accounting_id}\t{str(json_ser[0]['SerialNumber'])}\tбыло хорошо"
                else:
                    print(f"{line['asset_tag']}\t{str(json_ser[0]['SerialNumber'])}\tметка не соответствует")
                    string = [line['asset_tag'], line['serial'], 'метка не соответствует']
                    errors.append(string)
        pprint(errors)
        self.sheet.temp(errors)

    def hard_add_sn(self, reader):  # вроде робит
        errors = []
        for line in reader:
            data = {
                'sapid': f"$filter=AccountingId eq '{line['asset_tag']}'",
                'serial': f"$filter=SerialNumber eq '{line['serial']}'"
            }
            url = f"{self.api_domain}/api/hardware-items?"
            r_sap = requests.get(url + data['sapid'], cookies=self.cookies)
            json_sap = json.loads(r_sap.text)
            try:
                accounting_id = str(json_sap[0].get('AccountingId', 'хуй'))
            except KeyError:
                print(f"{line['asset_tag']}\t{line['serial']}\tчто блядь?")
                string = [line['asset_tag'], line['serial'], 'что блядь?']
                errors.append(string)
            except IndexError:
                print(f"{line['asset_tag']}\t{line['serial']}\tнетю")
                string = [line['asset_tag'], line['serial'], 'нетю']
                errors.append(string)
            else:
                url = f"{self.api_domain}/api/accountings/{line['asset_tag'].upper()}/serial/{line['serial'].upper()}"
                r = requests.put(url, cookies=self.cookies)
                if r.status_code == 200:
                    print(f"{str(json_sap[0]['AccountingId'])}\t{line['serial']}\tисправил жоско")
                    strong = f"{str(json_sap[0]['AccountingId'])}\t{line['serial']}\tстало хорошо"
                else:
                    print(url)
                    print(f"{line['asset_tag']}\t{r.status_code}\t{json.loads(r.text)['Message']}")
                    string = [line['asset_tag'], line['serial'], json.loads(r.text)['Message']]
                    errors.append(string)
        pprint(errors)

    def change_mac_addresses(self, reader):
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

            url = f"{self.api_domain}/api/accountings/{line['asset_tag']}/interfaces"
            payload = [
                {
                    "Name": "mngt",
                    "HardwareAddress": mac
                }
            ]
            r = requests.put(url, cookies=self.cookies, data=json.dumps(payload), headers=self.headers)
            print(f"{r.status_code}\t'{json.loads(r.text)['Message']}'")
            # r = requests.delete(url, cookies = auth.cookies, headers = auth.headers)
            if r.status_code != 200:
                print('')
                print(f"{r.status_code}\t'{json.loads(r.text)['Message']}'")
            else:
                print('.', end='')
        print('\n\tэрон дон доне')

    def change_network_roles(self, reader):
        hh = {
            6704: ["edge", 150],
            6: ["mngt_row", 240],
            662: ["mngt_row", 250]
        }
        for line in reader:
            url = f"{self.api_domain}/api/hosts?$filter=HostName eq '{line['new_name']}'"
            r = requests.get(url, cookies=self.cookies)
            json_1 = json.loads(r.text)
            # получаем необходимые данные
            host_id = json_1[0]['Id']
            hardware_model_id = json_1[0]['HardwareModelId']
            url = f"{self.api_domain}/api/hosts/{host_id}/change-network-roles"
            payload = {"Roles": [{"Name": hh[hardware_model_id][0], "IsPrimary": True}]}
            r = requests.put(url, cookies=self.cookies, data=json.dumps(payload), headers=self.headers)
            if r.status_code != 200:
                print(f"{r.status_code}\t'{json.loads(r.text)['Message']}'")

    # def set_work_status(self, reader):
    #     for line in reader:
    #         url = f"{self.api_domain}/api/hosts?$filter=HostName eq '{line['new_name']}'"
    #         r = requests.get(url, cookies=self.cookies)
    #         json_1 = json.loads(r.text)
    #         try:
    #             hostId = str(json_1[0]["Id"])
    #         except IndexError:
    #             print(f"{line['new_name']} - не в стойке")
    #         else:
    #             url = f"{self.api_domain}/api/hosts/{hostId}/set-work-status"
    #             # url = f"{auth.api_domain}/api/hosts/{hostId}/set-production-status"
    #             day_ta = datetime.datetime.today() + datetime.timedelta(days=1)
    #             # print(day_ta.strftime("%Y-%m-%d"))
    #             payload = {"DueDate": f"{day_ta.strftime('%Y-%m-%d')}","WorkTask": line['task']}
    #             r = requests.post(url, cookies=self.cookies, data=json.dumps(payload), headers = self.headers)
    #             # r = requests.post(url, cookies = auth.cookies, headers = auth.headers)
    #             if r.status_code != 200:
    #                 print(f"{line['new_name']}\t{r.status_code}\t'{json.loads(r.text)['Message']}'")

    def remove_hosts_by_sap(self, reader):
        messages = []
        for line in reader:
            url = f"{self.api_domain}/api/hosts?$filter=SapInventory eq '{line['asset_tag']}'"
            r = requests.get(url, cookies=self.cookies)
            json_1 = json.loads(r.text)
            try:
                host_id = str(json_1[0]["Id"])
                host_name = str(json_1[0]["HostName"])
            except IndexError:
                messages.append(f"\n{line['asset_tag']} - не в стойке")
                print('`', end='')
            else:
                url = f"{self.api_domain}/api/hosts/{host_id}"
                payload = {"Task": line['task']}
                r = requests.delete(url, cookies=self.cookies, data=json.dumps(payload), headers=self.headers)
                messages.append(f"{host_name} {line['asset_tag']} - удалён")
                print('.', end='')
        print('\n')
        pprint(messages)

    def remove_hosts_by_name(self, reader):
        messages = []
        for line in reader:
            url = f"{self.api_domain}/api/hosts?$filter=HostName eq '{line['new_name']}'"
            r = requests.get(url, cookies=self.cookies)
            json_1 = json.loads(r.text)
            try:
                host_id = str(json_1[0]["Id"])
                host_name = str(json_1[0]["HostName"])
            except IndexError:
                messages.append(f"{line['new_name']} - не в стойке")
                print('`', end='')
            else:
                url = f"{self.api_domain}/api/hosts/{host_id}"
                payload = {"Task": line['task']}
                r = requests.delete(url, cookies=self.cookies, data=json.dumps(payload), headers=self.headers)
                messages.append(f"{host_name} - удалён")
                print('.', end='')
        print('\n')
        pprint(messages)

    def get_parent_for_nodes(self, reader):
        list_ = []
        for line in reader:
            line.update({'fat_name': utils.get_fat_name(line['new_name'])})
            line, sap_id = self.get_data_from_id(line['asset_tag'], line)
            line, group = self.get_data_from_host(line['new_name'], line)
            list_.append(line)
        hh = {}
        for line in list_:
            if hh.get(line['fat_name'], 0) == 0:
                hh.update({line['fat_name']: {}})
                hh[line['fat_name']].update({'nodes': [line]})
                free_slots, parent_host_id = self.check_blade(line)
                hh[line['fat_name']].update({
                    'payload': {
                        'TemplateName': line['TemplateName'],
                        'OrgUnitId': line['OrgUnitId'],
                        'DataCenterId': line['DataCenterId'],
                        'InstallationTask': line['task'],
                        'HardwareModelId': line['HardwareModelId'],
                        'ParentHostId': parent_host_id,
                        'BladeSlotList': free_slots,
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
                empty = empty - 1
                arr.pop()
        return hh

    def check_blade(self, line):
        url = '{}/api/templates/host-blades?orgUnitId={}&dataCenterId={}&freeSlots=True&$filter=Name eq \'{}\''.format(
            self.api_domain,
            line['OrgUnitId'],
            line['DataCenterId'],
            line['fat_name'],
        )
        r = requests.get(url, cookies=self.cookies)
        json_1 = json.loads(r.text)[0]
        return json_1['FreeSlots'], json_1['Id']

    def make_to_plan_node(self, read):
        reader = {
            'to work': read,  # отфильтрованы только нужные
            'check': [],  # на проверке
            'error': [],  # какие-то ошибки
            'ok': [],  # всё хорошо
        }
        hh = self.get_parent_for_nodes(reader['to work'])
        line = ''
        for key in hh.keys():
            len_ = 0
            for line in hh[key]['nodes']:
                len_ = len_ + int(len(self.check_host(line['new_name'])))
            if len_ == 0:
                pprint('{} и {} хост(а) пошли'.format(
                    key,
                    len(hh[key]['nodes']),
                ))
                hh[key] = self.plan_create(hh[key]['payload'], hh[key])
            else:
                line.update({'error': 'дубликат хоста'})
        print('присваиваем метки')
        for key in hh.keys():
            self.set_sap_id(hh[key]['nodes'])

        print('переименовываем серверы')
        for key in hh.keys():
            self.rename_hosts(hh[key]['nodes'])
        pprint(hh)

    def make_office_switch(self, reader):  # свичи в офис
        array = []
        array_ok = []
        hh = {
            6704: ["edge", 150],
            6: ["mngt_row", 250],
            662: ["mngt_row", 250]
        }
        address = ''
        for line in reader:
            if line.get('unit', 'хуй') == 'хуй':
                line.update({'row': line['new_name'][3:6]})
                line.update({'rack': line['new_name'][3:7]})
            # чешем адрес
            if address == '':
                address = f"182.1{int(int(line['task'][-4:-3]) / 2)}.{int(int(line['task'][-4:-3]) / 4)}.{int(int(line['task'][-3:]) / 20)}"
            address = address.split('.')
            address.append(str(int(address.pop(3)) + 1))
            address = '.'.join(address)
            # print(address)
            payload = {
                'TemplateName': 'хуй',  # имя шаблона (тип хоста), обязательное поле
                'NetworkType': 'хуй',
                # тип устройства, соответствует атрибуту модели HardwareSubType, обязательное поле
                'OrgUnitId': 'хуй',
                # для какого проекта создается хост (здесь и ниже используется уникальный идентификатор оргюнита в системе CMDB), обязательное поле
                'HardwareModelId': 'хуй',  # уникальный идентификатор модели в системе CMDB, обязательное поле
                'InstallationTask': line['task'],  # задача, по которой устанавливается оборудование, обязательное поле
                'DataCenterId': 'хуй',  # уникальный идентификатор датацентра в системе CMDB, обязательное поле
                'DataCenterRackId': 'хуй',  # уникальный идентификатор стойки в системе CMDB, обязательное поле
            }
            if line['new_name'][:3] == 'eva':
                url = "{}/api/hosts?$filter=DataCenterRackName eq '{}'&$top=1".format(
                    self.api_domain,
                    line['rack']
                )
                # print(url)
                r = requests.get(url, cookies=self.cookies)
                json_1 = json.loads(r.text)
                line.update({'unit': utils.position(line['new_name'], json_1[0].get('DataCenterName', 'хуй'))})
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
                    self.api_domain,
                    loca_tion,
                    line['row'],
                )
                r = requests.get(url, cookies=self.cookies)
                json_1 = json.loads(r.text)
            payload.update({'FirstUnit': int(line['unit'])})
            if len(json_1) == 0:
                # получаем номер локации
                url = "{}/api/data-center-locations?$filter=Name eq '{}'".format(
                    self.api_domain,
                    line['new_name'].split('-')[0].upper()
                )
                r = requests.get(url, cookies=self.cookies)
                json_1 = json.loads(r.text)
                # получаем номер нужного цода в локации
                url = "{}/api/data-center-locations/{}/data-centers".format(
                    self.api_domain,
                    json_1[0].get('Id', 'хуй')
                )
                r = requests.get(url, cookies=self.cookies)
                json_1 = json.loads(r.text)
                # пишем
                payload.update({'DataCenterId': json_1[0].get('Id', 'хуй')})
                # получаем ряд
                url = "{}/api/data-centers/{}/rows?$top=1".format(
                    self.api_domain,
                    json_1[0].get('Id', 'хуй')
                )
                r = requests.get(url, cookies=self.cookies)
                json_1 = json.loads(r.text)
                # получаем стойку
                url = "{}/api/data-centers/rows/{}/racks?$filter=Name eq '{}'".format(
                    self.api_domain,
                    json_1[0].get('Id', 'хуй'),
                    line['rack']
                )
                r = requests.get(url, cookies=self.cookies)
                json_1 = json.loads(r.text)
                # пишем
                payload.update({'OrgUnitId': json_1[0].get('OrgUnits', 'хуй')[0]})
            else:
                payload.update({'DataCenterId': json_1[0].get('DataCenterId', 'хуй')})
                url = "{}/api/data-centers/rows/{}/racks?$filter=Name eq '{}'".format(
                    self.api_domain,
                    json_1[0].get('DataCenterRowId', 'хуй'),
                    line['rack']
                )
                r = requests.get(url, cookies=self.cookies)
                json_1 = json.loads(r.text)
                # пишем
                payload.update({'OrgUnitId': json_1[0]['OrgUnits'][0]})

            if payload['DataCenterId'] == 'хуй' or payload['OrgUnitId'] == 'хуй':
                print(f"что-то не так с локацией")
            else:
                url = "{}/api/data-centers/{}/rows".format(
                    self.api_domain,
                    payload['DataCenterId']
                )
                # print(url)
                r = requests.get(url, cookies=self.cookies)
                json_1 = json.loads(r.text)
                for i in json_1:
                    if i.get('Name', 'хуй') == line['row'].upper() and payload['DataCenterRackId'] == 'хуй':
                        payload.update({'DataCenterRackId': i['RackIds'][int(line['rack'].split(' ')[0][-2:]) - 1]})
                if payload['DataCenterRackId'] == 'хуй':
                    print(f"что-то не так cо стойкой")
                else:
                    url = "{}/api/hosts?$filter=HostName eq '{}'".format(
                        self.api_domain,
                        line['new_name']
                    )
                    r = requests.get(url, cookies=self.cookies)
                    json_1 = json.loads(r.text)
                    if len(json_1) == 0:
                        # из метки получаем необходимые данные
                        url = "{}/api/hardware-items?$filter=AccountingId eq '{}'".format(
                            self.api_domain,
                            line['asset_tag']
                        )
                        r = requests.get(url, cookies=self.cookies)
                        json_1 = json.loads(r.text)
                        payload.update({'TemplateName': json_1[0]['HardwareTypeName']})
                        payload.update({'NetworkType': json_1[0]['HardwareSubTypeName']})
                        payload.update({'HardwareModelId': json_1[0]['HardwareModelId']})
                        payload.update({'BalanceUnitId': int(json_1[0]['BalanceUnitId'])})
                        if payload.get('TemplateName') == 'Network':
                            payload.update({'Ip': address})
                            # чекаем атрибуты
                            url = "{}/api/hardware-models?$top=1&$expand=Attributes&$filter=Name eq '{}'".format(
                                self.api_domain,
                                json_1[0]['HardwareModelName']
                            )
                            r = requests.get(url, cookies=self.cookies)
                            json_1 = json.loads(r.text)
                            # вынимаем роль
                            for i in json_1[0]['Attributes']:
                                if i.get('Name', 'хуй') == 'Network Roles':
                                    payload.update({'NetworkRoles': [i.get('TextValue').split(',')[0].strip()]})
                        if payload.get('TemplateName') == 'Blade':
                            # по хорошему стоит проверить ноды на складе, но пока так
                            payload.update({'BladeServerHardwareModelId': 6119})
                        # print(f"{line['new_name']}\t{line['unit']}\t")
                        # pprint(payload)
                        print(f"{line['new_name']}\t{line['unit']}\t", end='')
                        url = f"{self.api_domain}/api/hosts"
                        r = requests.post(url, cookies=self.cookies, data=json.dumps(payload), headers=self.headers)
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
        self.sheet.temp(array_ok)
        # rename_hosts(array)

    # тестовая выгрузка зипа
    def get_zip_2(self):
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
        select_ = ''
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
        filter_ = ''
        for x in conditions:
            filter_ = filter_ + x
        url = f"{self.api_domain}/api/hardware-items?$select={select_}&$filter={filter_}&$orderby=HardwareModelName asc"
        print(url)
        r = requests.get(url, cookies=self.cookies)
        json_1 = json.loads(r.text)
        dict_ = {}  # этап 1 считаем
        for x in json_1:  # суммируем уникальные ключи
            if x.get('OrgUnitId') != 198:  # игнорируем офис
                if dict_.get(json.dumps(x), 0) == 0:  # если ключ уникальный
                    dict_.update([(json.dumps(x), 1)])  # добавляем его в хеш со значением один
                else:  # иначе
                    dict_[json.dumps(x)] += 1  # увеличиваем значение ключа на еденицу
        list_ = []  # этап 2 собираем
        for x in dict_.items():  # перебераем получившиеся пары
            y = json.loads(x[0])  # парсим хеш ключа
            y.update([('Quantity', x[1])])  # и дописываем в него количество
            list_.append(y)  # получившееся дописываем в массив
        list_2 = []  # этап 3 генерим данные для записи в таблицу
        for x in list_:
            sap_material = f"000{x.get('SAPMaterialNumber')}"
            sap_material = sap_material[-4:]
            y = [
                sap_material, str(x.get('HardwareModelId')),
                f"{x.get('HardwareTypeName')} {x.get('HardwareSubTypeName')}",
                x.get('HardwareModelName'),
                x.get('Quantity'),
                x.get('DataCenterLocationName'),
                x.get('DataCenterName')
            ]
            list_2.append(y)
        pprint(list_2)

    @staticmethod
    def get_hwmodelid():
        # по хорошему стоит проверять ноды на складе но пока так
        return 6119

    @staticmethod
    def get_ip_address():
        # нужно как-то научиться чекать свободные адреса
        string = '192.168.0.0'
        return string

    def get_data_from_host(self, hostname, payload):
        loca, group, row, rack = utils.get_location(hostname, payload.get('TemplateName'))
        # получаем номер локации:
        url = "{}/api/data-center-locations?$filter=Name eq '{}'".format(
            self.api_domain,
            loca,  # нужно получить из имени
        )
        r = requests.get(url, cookies=self.cookies)
        json_1 = json.loads(r.text)
        # номер локации
        data_center_location_id = json_1[0].get('Id', 'хуй')
        payload.update({'DataCenterLocationId': data_center_location_id})
        # получаем номер нужного цода в локации:
        url = "{}/api/data-center-locations/{}/data-centers?$filter=Name eq '{}'".format(
            self.api_domain,
            payload.get('DataCenterLocationId'),
            group,  # нужно получить из имени
        )
        r = requests.get(url, cookies=self.cookies)
        json_1 = json.loads(r.text)
        # номер цода
        data_center_id = json_1[0].get('Id', 'хуй')
        payload.update({'DataCenterId': data_center_id})
        # получаем номер ряда
        url = "{}/api/data-centers/{}/rows?$filter=Name eq '{}'".format(
            self.api_domain,
            data_center_id,
            row,  # нужно получить из имени
        )
        # print(url)
        r = requests.get(url, cookies=self.cookies)
        json_1 = json.loads(r.text)
        # номер ряда
        data_center_row_id = json_1[0].get('Id', 'хуй')
        payload.update({'DataCenterRowId': data_center_row_id})
        # получаем номер и юнит стойки
        url = "{}/api/data-centers/rows/{}/racks?$filter=Name eq '{}'".format(
            self.api_domain,
            data_center_row_id,
            rack,  # нужно получить из имени
        )
        r = requests.get(url, cookies=self.cookies)
        json_1 = json.loads(r.text)
        # номер стойки
        data_center_rack_id = json_1[0].get('Id', 'хуй')
        payload.update({'DataCenterRackId': data_center_rack_id})
        # номер оргЮнита
        org_unit_id = json_1[0].get('OrgUnits', 'хуй')[0]
        payload.update({'OrgUnitId': org_unit_id})
        return payload, group

    def get_data_from_id(self, asset_tag, payload):
        sap_id = self.check_id(asset_tag)
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
            payload.update({'Ip': self.get_ip_address()})
            if payload.get('NetworkType') == 'Switch':
                # роль свича
                payload.update({'NetworkRoles': self.get_role(sap_id['HardwareModelName'])})
        if payload.get('TemplateName') == 'Blade':
            # молель нод
            payload.update({'BladeServerHardwareModelId': self.get_hwmodelid()})
        if payload.get('TemplateName') == 'Server':
            # количество серверов
            payload.update({'HostQuantity': 1})
        return payload, sap_id

    def check_id(self, asset_tag):
        url = "{}/api/hardware-items?$filter=AccountingId eq '{}'".format(
            self.api_domain,
            asset_tag
        )
        r = requests.get(url, cookies=self.cookies)
        json_1 = json.loads(r.text)
        return json_1[0]

    def check_host(self, hostname):
        url = "{}/api/hosts?$filter=HostName eq '{}'".format(
            self.api_domain,
            hostname
        )
        r = requests.get(url, cookies=self.cookies)
        json_1 = json.loads(r.text)
        return json_1

    def get_role(self, name):
        url = "{}/api/hardware-models?$top=1&$expand=Attributes&$filter=Name eq '{}'".format(
            self.api_domain,
            name
        )
        r = requests.get(url, cookies=self.cookies)
        json_1 = json.loads(r.text)
        for i in json_1[0]['Attributes']:
            if i.get('Name', 'хуй') == 'Network Roles':
                return [i.get('TextValue').split(',')[0].strip()]

    # тут собирается запрос
    def plan_make_payload(self, line):
        payload = {}
        payload.update({'InstallationTask': line.get('task', '')})
        payload.update({'CustomHostName': line.get('new_name', '')})
        if line['asset_tag'] == '':
            line.update({'error': 'нет метки'})
            return payload, line
        else:
            payload, sap_id = self.get_data_from_id(line['asset_tag'], payload)
        location = sap_id['DataCenterLocationName']
        if line['new_name'] != '' and location == 'ICVA':
            payload, group = self.get_data_from_host(line['new_name'], payload)
            try:
                unit = int(line.get('unit', '').split(' ')[0])
            except ValueError:
                line.update({'unit': ''})
            else:
                line.update({'unit': unit})
            if line.get('unit', '') == '' and payload.get('TemplateName') == 'Server':
                line.update({'unit': utils.position(line['new_name'], group)})
                payload.update({'FirstUnit': line['unit']})
            elif type(line['unit']) is int:
                payload.update({'FirstUnit': line['unit']})
        elif line['new_name'] == '':
            line.update({'error': 'нет имени хоста'})
        else:
            line.update({'error': 'железка где-то не там: {}'.format(location)})
        return payload, line

    # тут запрос отправляется
    def plan_create(self, payload, line):
        url = '{}/api/hosts'.format(self.api_domain)
        r = requests.post(url, cookies=self.cookies, data=json.dumps(payload), headers=self.headers)
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

    def plan_test(self, read):
        reader = {
            'to work': read,  # отфильтрованы только нужные
            'check': [],  # на проверке
            'error': [],  # какие-то ошибки
            'ok': [],  # всё хорошо
        }
        # print(reader['to work'])
        for line in reader['to work']:
            payload, line = self.plan_make_payload(line)
            print(line)
            pprint(payload)
            if line.get('error', 0) != 0:
                reader['error'].append(line)
            elif len(self.check_host(line['new_name'])) == 0:
                print('запрос', end=' ')
                tic = time.perf_counter()
                reader['check'].append(self.plan_create(payload, line))
                toc = time.perf_counter()
                print(str(toc - tic), end=' ')
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
        pprint(reader['ok'])

        print('присваиваем метки')
        self.set_sap_id(reader['ok'])
        # print('начинаем обратный отсчёт')
        # for i in range(300,0,-1):
        #     sys.stdout.write(str(i)+' ')
        #     sys.stdout.flush()
        #     time.sleep(1)
        print('переименовываем серверы')
        # kick.rename_sap(auth, reader['ok'])
        self.rename_hosts(reader['ok'])
