import requests, json, getpass, os, platform
from pykeepass import PyKeePass
from pathlib import Path

if not os.path.isdir('temp'):
     os.mkdir('temp')

class authentication():
    def __init__(self): # получаем печеньки из файла
        self.my_base = ''
        if os.path.exists('temp/api_domain') is False:
            if self.my_base == '':
                self.my_base = base()
            self.api_domain = self.my_base.entry.notes
            file = open('temp/api_domain', 'w')
            file.write(self.api_domain)
            file.close()
        else:
            file = open('temp/api_domain', 'r')
            self.api_domain = file.read()
            file.close()
        self.headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
        if os.path.exists('temp/cookies.json') is False:
            self.user_data = ''
            self.cookies = {"Name": "Value"}
        else:
            file = open('temp/cookies.json', 'r')
            self.user_data = json.loads(file.read())
            file.close()
            self.cookies = {self.user_data.get('Name','huy'): self.user_data.get('Value','huy')}
        if os.path.exists('temp/credentials.json') is False:
            if self.my_base == '':
                self.my_base = base()
            data_ta = str(self.my_base.credentials.data)
            data_ta = data_ta[2:-1].split('\\n')
            file = open('temp/credentials.json', 'w')
            for i in data_ta:
                file.write(i+'\n')
            file.close()

    def check_access(self):
        url = f"{self.api_domain}/api/hosts?$filter=DataCenterRackName eq '604'&$top=1"
        r = requests.get(url, cookies=self.cookies)
        # print(r.status_code)
        return r.status_code

    def get_new_cookies(self):
        if self.my_base == '':
            self.my_base = base()
        status_code = 1
        url = f"{self.api_domain}/api/login"
        while status_code != 200:
            payload = self.my_base.make_payload()
            r = requests.post(url, data=json.dumps(payload), headers=self.headers)
            self.user_data = json.loads(r.text)
            self.user_data.update([("UserName",payload.get('Name'))])
            if self.user_data.get('Name', 'хуй') != 'хуй':
                self.cookies = {self.user_data.get('Name'): self.user_data.get('Value')}
            file = open('temp/cookies.json', 'w')
            file.write(json.dumps(self.user_data))
            file.close()
            status_code = r.status_code
        print('свежие куки получены')

class base():
    def __init__(self):
        list_h = {}
        home_path = {
            'Linux': '~/', 'Darwin': '~/',
            'Windows': f"C:\\Users\\{getpass.getuser()}\\" # спасибо Хику за это
        }
        result = list(Path(os.path.expanduser(home_path[platform.system()])).rglob("*.kdbx"))
        y = 1
        for i in result:
            list_h[y] = i
            y += 1
        if len(list_h.keys()) == 1:                     # если база одна
            for i in list_h.values():
                path_of_base = i
                print(f"выбрана база:\n\t{path_of_base}")
        elif len(list_h.keys()) > 1:                    # если баз нашлось больше чем одна
            print(f"нашлось несколько баз:")
            for i in list_h.keys():
                print(f"\t{i} - {list_h[i]}")
            path_of_base = list_h[int(input('\nвведи номер базы из списка: ').strip())]
            print(f"выбрана база:\n\t{path_of_base}")
        else:                                           # если ничего не нашлось
            path_of_base = input('\n\tу вас должна быть создана база данных с паролями *.kdbx\n\tиначе ничего не получится\n\t').strip()
            print(f"выбрана:\n\t{path_of_base}")
        kp = PyKeePass(os.path.expanduser(path_of_base), password=getpass.getpass(prompt='\n\tпароль от БД:'))
        self.entry = kp.find_entries(url='ra.ma*', regex=True, first=True)
        if len(kp.find_attachments(filename='credentials.json')) == 1:
            self.credentials = self.entry.attachments[0]
        elif len(kp.find_attachments(filename='credentials.json')) > 1:
            print('решения, как быть дальше, пока нет')
            exit()
        else:
            print('не хватает файлика')
            exit()

    def make_payload(self):
        if len(self.entry.custom_properties.keys()) == 1:    # если токен один
            for i in self.entry.custom_properties.values():
                otpPassword = i + input('\n\tцифры с ОТП: ').strip()
        else:                                           # если токенов больше чем один
            list_h = {}
            y = 1
            for i in self.entry.custom_properties.keys():
                list_h[y] = i
                y += 1
            print(f"нашлось несколько токенов:")
            for i in list_h.keys():
                print(f"\t{i} - {list_h[i]}")
            _token = ''
            while _token == '':
                token_ = int(input('\nвыбери из списка: ').strip())
                if list_h.get(token_, 'хуй') == 'хуй':
                    print('\t>>>номер не корректный<<<')
                else:
                    _token = self.entry.custom_properties.get(list_h.get(token_, 'хуй'), 'хуй')
                    otpPassword = _token + input('\n\tцифры с ОТП: ').strip()
        payload = {
            "Name" :self.entry.username,
            "DomainPassword" :self.entry.password,
            "OtpPassword" : otpPassword
        }
        return payload
