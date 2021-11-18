from __future__ import print_function
from sheets import sheets
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file temp/token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

spreadsheet_id = {
    'temp': sheets.sheets_data['temp'][0],
    'servers': sheets.sheets_data['servers'][0],
    'accounting': [sheets.sheets_data['accounting'][0],'Итог смены!I2:O'],
    'stock': sheets.sheets_data['stock'][0],
    }
range_name = ['InfraM!A1:E','InfraM!A1:H']

def infra():
    hh = sheets.mega_auth()

    request = hh['service'].spreadsheets().values().get(
        spreadsheetId=spreadsheet_id['temp'], range=range_name[1],
        valueRenderOption=hh['value_render_option'],
        dateTimeRenderOption=hh['date_time_render_option']).execute()
    values = request.get('values', [])
    # print(request)
    if not values:
        print('No data found.')
    else:   #собираем список словарей (массив хешей)
        dick = []
        for row in values[1:]:
            string = dict(zip(values[0], row))
            dick.append(string)
        # pprint(dick)
        return dick

def smart(name, num):
    hh = sheets.mega_auth()

    request = hh['service'].spreadsheets().values().get(
        spreadsheetId=spreadsheet_id[name][0],
        range=spreadsheet_id[name][num] if type(num) is int else num,
        valueRenderOption=hh['value_render_option'],
        dateTimeRenderOption=hh['date_time_render_option']).execute()
    values = request.get('values', [])
    # print(request)
    if not values:
        print('No data found.')
    else:   #собираем список словарей (массив хешей)
        if type(num) is str:
            return values[1:]
        else:
            dick = []
            for row in values[1:]:
                string = dict(zip(values[0], row))
                if string.get(':-)', '') == 'TRUE' or string.get(':-(', '') == 'TRUE':
                    dick.append(string)
            # pprint(dick)
            return dick

def another():   #собираем словарь эназерпрожекторных тасков
    hh = sheets.mega_auth()
    # for xx in ['another!A2:B']:
    for xx in ['temp!A2:B']:
        request = hh['service'].spreadsheets().values().get(
            # spreadsheetId = sheets.sheets_data['servers'][0],
            spreadsheetId = spreadsheet_id['accounting'][0],
            range = xx,
            valueRenderOption = hh['value_render_option'],
            dateTimeRenderOption = hh['date_time_render_option']).execute()
    values = request.get('values', [])
    if not values:
        print('No data found.')
    else:
        dick = {}
        for row in values:
            dick.update({row[0]:row[1]})
        return dick