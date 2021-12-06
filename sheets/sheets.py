from __future__ import print_function
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
    'stickers_data':[ # наклейки
        '1LmR2SUtVsw6DnqiQZ9LxWNlIJ7DJs2OKjNCssJo4Sms',
        {
            0: ['Лист1!A1:E'],
            }
    ],
    'stock':[ # запасные комплектующие
        '1wbn-NkP5Q2XDyhG7nNODZCia_kNXOOvmOb4evBLHvao',
        {
            0: 'выгрузка!I3:L',
            1: 'выгрузка!A1',
            2: 'выгрузка!A3:G',
            3: '',
            }
    ],
    'servers':[ # файл с серверами
        '1LCzfHK38xDHcA6L0UYn0FzsR0LQ0cN5fVhCtOOFRX8U',
        {
            0: 'from_cmdb!A3:K', # сюда пишет всё по осам
            1: 'hot zip!A3:K', # сюда пишет горячий зип
            2: 'on 5 floor!A3:K', # сюда пишет сервера на складе
            3: 'another project!A3:F', # сюда пишет эназерпрожектные осы
            4: 'another project!G3:H', # отсюда берёт соотношение таска к проекту
            }

    ],
    'temp':[ # work hard
        '1FwmGUPSRfjadGwJzUtyX4mc-nxKt5xtGWMdm_rEEe2w',
        {
            0: ['temp!A2:C'],
            1: 'InfraM!A1:E',
            }
    ],
    'accounting':[ # учёт комплектующих
        '1qCvkrLOWw2rSmMZSEKnN62KPwagyw44hU--wqOwzb-g',
        {
            0: ['materials!A3:D'],
            1: ['materials!P3:Q'],
            2: 'materials!S3:T',
            3: 'Итог смены!I2:O',
            4: 'temp!a1:b',
            }
    ],
    'hw_models':[ # 
        '1ijPWH99k6B1mVCZ5WzuEFFPhQFrYh5UNXYOovk-Sj4Y',
        {
            0: 'Лист1!A2:E',
            1: 'Лист4!A2:G',
            }
    ],
    'test':[ # 
        '1vzjAqnVwXvZKIicurcvZNcoiQTScEOLF7sF4_ClvHis',
        {
            0: 'servers!A2:E',
            1: 'Лист4!A2:G',
            }
    ],
}

def mega_auth():
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
        'value_input_option': ['RAW','USER_ENTERED'],
        'clear_values_request_body': {
            # TODO: Add desired entries to the request body.
            }
    }

    return mega_auth_hh
