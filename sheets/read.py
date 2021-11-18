from __future__ import print_function
from sheets import sheets
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def infra():
    hh = sheets.mega_auth()

    request = hh['service'].spreadsheets().values().get(
        spreadsheetId=sheets.data['temp'][0], range=sheets.data['temp'][1][1],
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
    """если номер, то берём диапазон из списка"""
    range_ = sheets.data[name][1][num] if type(num) is int else num
    request = hh['service'].spreadsheets().values().get(
        spreadsheetId=sheets.data[name][0], range=range_,
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
                elif string.get(':-)', '') == '' and string.get(':-(', '') == '':
                    dick.append(row)
            # pprint(dick)
            return dick

def another():   #собираем словарь эназерпрожекторных тасков
    hh = sheets.mega_auth()
    request = hh['service'].spreadsheets().values().get(
        spreadsheetId = sheets.data['accounting'][0],
        range = sheets.data['accounting'][1][4],
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