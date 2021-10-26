from __future__ import print_function
from sheets import sheets
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file temp/token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

spreadsheet_id = '1FwmGUPSRfjadGwJzUtyX4mc-nxKt5xtGWMdm_rEEe2w'
range_name = ['InfraM!A1:E']

def infra():
    hh = sheets.mega_auth()

    request = hh['service'].spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name[0],
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

def another():   #собираем словарь эназерпрожекторных тасков
    hh = sheets.mega_auth()
    # for xx in ['another!A2:B']:
    for xx in ['temp!A2:B']:
        request = hh['service'].spreadsheets().values().get(
            # spreadsheetId = sheets.sheets_data['servers'][0],
            spreadsheetId = '1qCvkrLOWw2rSmMZSEKnN62KPwagyw44hU--wqOwzb-g',
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

def install():
    hh = sheets.mega_auth()
    for xx in ['Итог смены!J2:N']:
        request = hh['service'].spreadsheets().values().get(
            spreadsheetId = sheets.sheets_data['accounting'][0],
            range = xx,
            valueRenderOption = hh['value_render_option'],
            dateTimeRenderOption = hh['date_time_render_option']).execute()
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