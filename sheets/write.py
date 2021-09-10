from __future__ import print_function
import datetime
from sheets import sheets
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def accounting(values,number): # выгружает данные о материалах
    hh = sheets.mega_auth()
    body = {
        'values': values
    }
    for xx in sheets.sheets_data['accounting'][1][int(number)]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.sheets_data['accounting'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.sheets_data['accounting'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()
    if int(number) == 0:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.sheets_data['stock'][0], range=sheets.sheets_data['stock'][1][0],
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.sheets_data['stock'][0], range=sheets.sheets_data['stock'][1][0],
            valueInputOption=hh['value_input_option'][0], body=body).execute()

def servers(values,number): # 
    hh = sheets.mega_auth()

    body = {
        'values': values
    }
    for xx in [sheets.sheets_data['servers'][1][int(number)]]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.sheets_data['servers'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.sheets_data['servers'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()

def temp(values): # выгружает временные данные
    hh = sheets.mega_auth()

    body = {
        'values': values
    }
    for xx in [sheets.sheets_data['temp'][1][0]]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.sheets_data['temp'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.sheets_data['temp'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()

def hw_models(values): # выгружает hw_models
    hh = sheets.mega_auth()

    body = {
        'values': values
    }
    for xx in [sheets.sheets_data['hw_models'][1][0]]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.sheets_data['hw_models'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.sheets_data['hw_models'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()

def stock(values): # выгружает данные по запасам
    hh = sheets.mega_auth()
    to_day_ta = datetime.datetime.today()

    body = {
        'values': [[to_day_ta.strftime("%d.%m.%Y")]]
    }
    request = hh['service'].spreadsheets().values().update(
        spreadsheetId=sheets.sheets_data['stock'][0], range=sheets.sheets_data['stock'][1][1],
        valueInputOption=hh['value_input_option'][0], body=body).execute()

    body = {
        'values': values
    }
    for xx in [sheets.sheets_data['stock'][1][2]]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.sheets_data['stock'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.sheets_data['stock'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()

def stickers_data(values): # выгружает данные для наклеек
    hh = sheets.mega_auth()

    body = {
        'values': values
    }
    for xx in [sheets.sheets_data['stickers_data'][1][0]]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.sheets_data['stickers_data'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.sheets_data['stickers_data'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()

# def _zip(values): # фиксирует расход (не работает)
#     hh = sheets.mega_auth()
#     ranges = {
#         'выгрузка!AJ3:AO':['выгрузка!AJ3:AM','выгрузка!AN3:AO'],
#         'выгрузка!H3:M':['выгрузка!H3:K','выгрузка!L3:M'],
#         }
#     body = {
#         'values': [[datetime.datetime.today().strftime("%d.%m.%Y")]]
#     }
#     request = hh['service'].spreadsheets().values().update(
#         spreadsheetId = sheets.sheets_data['stock'][0], range = 'выгрузка!AJ2',
#         valueInputOption = hh['value_input_option'][0], body = body).execute()
#     for xx in ranges.keys():
#         index = 0
#         request = hh['service'].spreadsheets().values().clear(
#             spreadsheetId = sheets.sheets_data['stock'][0],
#             range = xx,
#             body = hh['clear_values_request_body']).execute()
#         print(f"{xx} стёрто")
#         for value_part in values:
#             body = {
#                 'values': value_part
#             }
#             # for xx in [ranges[xx][index]]:
#             request = hh['service'].spreadsheets().values().update(
#                 spreadsheetId = sheets.sheets_data['stock'][0],
#                 range = ranges[xx][index],
#                 valueInputOption = hh['value_input_option'][index],
#                 body = body).execute()
#             print(f"{ranges[xx][index]} записано")
#             index+=1
