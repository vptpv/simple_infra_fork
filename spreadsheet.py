import os.path
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


# If modifying these scopes, delete the file temp/token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# The ID and range of a sample spreadsheet.
data = {
    'stickers_data': [  # наклейки
        '1LmR2SUtVsw6DnqiQZ9LxWNlIJ7DJs2OKjNCssJo4Sms',
        {
            0: ['Лист1!A1:E'],
            }
    ],
    'stock': [  # запасные комплектующие
        '1wbn-NkP5Q2XDyhG7nNODZCia_kNXOOvmOb4evBLHvao',
        {
            0: 'выгрузка!I3:L',
            1: 'выгрузка!A1',
            2: 'выгрузка!A3:G',
            3: '',
            }
    ],
    'servers': [  # файл с серверами
        '1LCzfHK38xDHcA6L0UYn0FzsR0LQ0cN5fVhCtOOFRX8U',
        {
            0: 'from_cmdb!A3:K',  # сюда пишет всё по осам
            1: 'hot zip!A3:K',  # сюда пишет горячий зип
            2: 'on 5 floor!A3:K',  # сюда пишет сервера на складе
            3: 'another project!A3:F',  # сюда пишет эназерпрожектные осы
            4: 'another project!G3:H',  # отсюда берёт соотношение таска к проекту
            }

    ],
    'temp': [  # work hard
        '1FwmGUPSRfjadGwJzUtyX4mc-nxKt5xtGWMdm_rEEe2w',
        {
            0: ['temp!A2:C'],
            1: 'InfraM!A1:E',
            }
    ],
    'accounting': [  # учёт комплектующих
        '1qCvkrLOWw2rSmMZSEKnN62KPwagyw44hU--wqOwzb-g',
        {
            0: ['materials!A3:D'],
            1: ['materials!P3:Q'],
            2: 'materials!S3:T',
            3: 'Итог смены!I2:O',
            }
    ],
    'hw_models': [  #
        '1ijPWH99k6B1mVCZ5WzuEFFPhQFrYh5UNXYOovk-Sj4Y',
        {
            0: 'Лист1!A2:E',
            1: 'Лист4!A2:G',
            }
    ],
    'test': [  #
        '1vzjAqnVwXvZKIicurcvZNcoiQTScEOLF7sF4_ClvHis',
        {
            0: 'servers!A2:E',
            1: 'Лист4!A2:G',
            }
    ],
}


class Sheet:
    def __init__(self):
        creds = None
        if os.path.exists('temp/token.json'):
            creds = Credentials.from_authorized_user_file('temp/token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if os.path.exists('temp/credentials.json'):
                    print('\nесли окно браузера не открылось, то сделай это сам и авторизуйся в рабочем гуглокаунте\n')
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'temp/credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                else:
                    print('\nсикретни файл отсутствует\n')
                    exit()
            # Save the credentials for the next run
            with open('temp/token.json', 'w') as token:
                token.write(creds.to_json())

        mega_auth_hh = {
            'service': build('sheets', 'v4', credentials=creds),
            'value_render_option': 'FORMATTED_VALUE',  # TODO: Update placeholder value.
            'date_time_render_option': 'FORMATTED_STRING',  # TODO: Update placeholder value.
            'value_input_option': ['RAW', 'USER_ENTERED'],
            'clear_values_request_body': {
                # TODO: Add desired entries to the request body.
            }
        }
        self.api = mega_auth_hh['service'].spreadsheets().values()
        self.value_render_option = mega_auth_hh['value_render_option']
        self.dt_render_option = mega_auth_hh['date_time_render_option']
        self.clear_values_request_body = mega_auth_hh['clear_values_request_body']
        self.value_input_option = mega_auth_hh['value_input_option']

    def read_another(self):  # собираем словарь эназерпрожекторных тасков
        # hh = sheets.mega_auth()
        # request = hh['service'].spreadsheets().values().get(
        request = self.api.get(
            spreadsheetId=data['servers'][0],
            range=data['servers'][1][4],
            valueRenderOption=self.value_render_option,
            dateTimeRenderOption=self.dt_render_option).execute()
        values = request.get('values', [])
        if not values:
            print('No data found.')
        else:
            dick = {}
            for row in values:
                dick.update({row[0]: row[1]})
            return dick

    def smart(self, name, num):
        # если номер, то берём диапазон из списка
        range_ = data[name][1][num] if type(num) is int else num
        request = self.api.get(
            spreadsheetId=data[name][0], range=range_,
            valueRenderOption=self.value_render_option,
            dateTimeRenderOption=self.dt_render_option).execute()
        values = request.get('values', [])
        # print(request)
        if not values:
            print('No data found.')
        else:  # собираем список словарей (массив хешей)
            if type(num) is str:
                return values[1:]
            else:
                dick = []
                for row in values[1:]:
                    string = dict(zip(values[0], row))
                    if string.get(':-)', '') == 'TRUE' or string.get(':-(', '') == 'TRUE':
                        dick.append(string)
                    elif string.get(':-)', '') == '' and string.get(':-(', '') == '':
                        dick.append(row)
                # pprint(dick)
                return dick

    def read_infra(self):
        request = self.api.get(
            spreadsheetId=data['temp'][0], range=data['temp'][1][1],
            valueRenderOption=self.value_render_option,
            dateTimeRenderOption=self.dt_render_option).execute()
        values = request.get('values', [])
        # print(request)
        if not values:
            print('No data found.')
        else:  # собираем список словарей (массив хешей)
            dick = []
            for row in values[1:]:
                string = dict(zip(values[0], row))
                dick.append(string)
            # pprint(dick)
            return dick

    def accounting(self, values, number):  # выгружает данные о материалах
        body = {
            'values': values
        }
        for xx in data['accounting'][1][int(number)]:
            request = self.api.clear(
                spreadsheetId=data['accounting'][0], range=xx,
                body=self.clear_values_request_body).execute()

            request = self.api.update(
                spreadsheetId=data['accounting'][0], range=xx,
                valueInputOption=self.value_input_option[0], body=body).execute()
        if int(number) == 0:
            request = self.api.clear(
                spreadsheetId=data['stock'][0], range=data['stock'][1][0],
                body=self.clear_values_request_body).execute()

            request = self.api.update(
                spreadsheetId=data['stock'][0], range=data['stock'][1][0],
                valueInputOption=self.value_input_option[0], body=body).execute()

    def servers(self, values, number):  #
        # hh = sheets.mega_auth()

        body = {
            'values': values
        }
        for xx in [data['servers'][1][int(number)]]:
            request = self.api.clear(
                spreadsheetId=data['servers'][0], range=xx,
                body=self.clear_values_request_body).execute()

            request = self.api.update(
                spreadsheetId=data['servers'][0], range=xx,
                valueInputOption=self.value_input_option[0], body=body).execute()

    def temp(self, values):  # выгружает временные данные
        body = {
            'values': values
        }
        for xx in [data['temp'][1][0]]:
            request = self.api.clear(
                spreadsheetId=data['temp'][0], range=xx,
                body=self.clear_values_request_body).execute()

            request = self.api.update(
                spreadsheetId=data['temp'][0], range=xx,
                valueInputOption=self.value_input_option[0], body=body).execute()

    def hw_models(self, values, number):  # выгружает hw_models
        body = {
            'values': values
        }
        for xx in [data['hw_models'][1][int(number)]]:
            request = self.api.clear(
                spreadsheetId=data['hw_models'][0], range=xx,
                body=self.clear_values_request_body).execute()

            request = self.api.update(
                spreadsheetId=data['hw_models'][0], range=xx,
                valueInputOption=self.value_input_option[0], body=body).execute()

    def stock(self, values):  # выгружает данные по запасам
        to_day_ta = datetime.datetime.today()

        body = {
            'values': [[to_day_ta.strftime("%d.%m.%Y")]]
        }
        request = self.api.update(
            spreadsheetId=data['stock'][0], range=data['stock'][1][1],
            valueInputOption=self.value_input_option[0], body=body).execute()

        body = {
            'values': values
        }
        for xx in [data['stock'][1][2]]:
            request = self.api.clear(
                spreadsheetId=data['stock'][0], range=xx,
                body=self.clear_values_request_body).execute()

            request = self.api.update(
                spreadsheetId=data['stock'][0], range=xx,
                valueInputOption=self.value_input_option[0], body=body).execute()

    def stickers_data(self, values):  # выгружает данные для наклеек
        body = {
            'values': values
        }
        for xx in [data['stickers_data'][1][0]]:
            request = self.api.clear(
                spreadsheetId=data['stickers_data'][0], range=xx,
                body=self.clear_values_request_body).execute()

            request = self.api.update(
                spreadsheetId=data['stickers_data'][0], range=xx,
                valueInputOption=self.value_input_option[0], body=body).execute()

    def write_another(self, values):  # выгружает эназерпрожекторные осы
        req_data = {
                'accounting': {
                    'id': data['accounting'][0],
                    'range': data['accounting'][1][2],
                    'body': {'values': values['accounting']}
                },
                'servers': {
                    'id': data['servers'][0],
                    'range': data['servers'][1][3],
                    'body': {'values': values['servers']}
                },
            }
        for xx in req_data.keys():
            # print(type(xx))
            request = self.api.clear(
                spreadsheetId=req_data[xx]['id'], range=req_data[xx]['range'],
                body=self.clear_values_request_body).execute()

            request = self.api.update(
                spreadsheetId=req_data[xx]['id'], range=req_data[xx]['range'],
                valueInputOption=self.value_input_option[0], body=req_data[xx]['body']).execute()

    def read_log(self):
        file = open('temp/base.log', 'r')
        list_hw_models = []
        for line in file:
            line = line.split("|")
            # print(len(line))
            list_hw_models.append(line[:-1])
        self.hw_models(list_hw_models, 1)
