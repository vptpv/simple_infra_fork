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
sheets_data = {
    'stickers_data':[ # наклейки
        '1LmR2SUtVsw6DnqiQZ9LxWNlIJ7DJs2OKjNCssJo4Sms',
        ['Лист1!A1:E']
    ],
    'stock':[ # запасные комплектующие
        '1wbn-NkP5Q2XDyhG7nNODZCia_kNXOOvmOb4evBLHvao',
        ['выгрузка!I3:L','выгрузка!A1','выгрузка!A3:G','']
        # 0               1             2               3
    ],
    'servers':[ # файл с серверами
        '1LCzfHK38xDHcA6L0UYn0FzsR0LQ0cN5fVhCtOOFRX8U',
        ['from_cmdb!A2:K','Hot!M2:W','Hot!A2:K']
        # 0                1          2
    ],
    'temp':[ # work hard
        '1FwmGUPSRfjadGwJzUtyX4mc-nxKt5xtGWMdm_rEEe2w',
        ['temp!A2:C']
    ],
    'accounting':[ # учёт комплектующих
        # '1TsGxlL1gz6XgybYwjdhZ1zQaNr6L1qRoiMZG2Hrr7Q0',
        '1qCvkrLOWw2rSmMZSEKnN62KPwagyw44hU--wqOwzb-g',
        [['materials!A3:D'],['materials!P3:Q']]
        # ['temp!A3:D']
    ],
    'hw_models':[ # 
        '1ijPWH99k6B1mVCZ5WzuEFFPhQFrYh5UNXYOovk-Sj4Y',
        ['Лист1!A2:E','Лист4!A2:G']
    ]
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
