import datetime
from sheets import sheets


def accounting(values, number):  # выгружает данные о материалах
    hh = sheets.mega_auth()
    body = {
        'values': values
    }
    for xx in sheets.data['accounting'][1][int(number)]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.data['accounting'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.data['accounting'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()
    if int(number) == 0:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.data['stock'][0], range=sheets.data['stock'][1][0],
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.data['stock'][0], range=sheets.data['stock'][1][0],
            valueInputOption=hh['value_input_option'][0], body=body).execute()


def servers(values, number):  #
    hh = sheets.mega_auth()

    body = {
        'values': values
    }
    for xx in [sheets.data['servers'][1][int(number)]]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.data['servers'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.data['servers'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()


def temp(values):  # выгружает временные данные
    hh = sheets.mega_auth()

    body = {
        'values': values
    }
    for xx in [sheets.data['temp'][1][0]]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.data['temp'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.data['temp'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()


def hw_models(values, number):  # выгружает hw_models
    hh = sheets.mega_auth()

    body = {
        'values': values
    }
    for xx in [sheets.data['hw_models'][1][int(number)]]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.data['hw_models'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.data['hw_models'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()


def stock(values):  # выгружает данные по запасам
    hh = sheets.mega_auth()
    to_day_ta = datetime.datetime.today()

    body = {
        'values': [[to_day_ta.strftime("%d.%m.%Y")]]
    }
    request = hh['service'].spreadsheets().values().update(
        spreadsheetId=sheets.data['stock'][0], range=sheets.data['stock'][1][1],
        valueInputOption=hh['value_input_option'][0], body=body).execute()

    body = {
        'values': values
    }
    for xx in [sheets.data['stock'][1][2]]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.data['stock'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.data['stock'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()


def stickers_data(values):  # выгружает данные для наклеек
    hh = sheets.mega_auth()

    body = {
        'values': values
    }
    for xx in [sheets.data['stickers_data'][1][0]]:
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=sheets.data['stickers_data'][0], range=xx,
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=sheets.data['stickers_data'][0], range=xx,
            valueInputOption=hh['value_input_option'][0], body=body).execute()


def another(values):  # выгружает эназерпрожекторные осы
    hh = sheets.mega_auth()
    data = {
            'accounting': {
                'id': sheets.data['accounting'][0],
                'range': sheets.data['accounting'][1][2],
                'body': {'values': values['accounting']},
            },
            'servers': {
                'id': sheets.data['servers'][0],
                'range': sheets.data['servers'][1][3],
                'body': {'values': values['servers']},
            },
        }
    for xx in data.keys():
        # print(type(xx))
        request = hh['service'].spreadsheets().values().clear(
            spreadsheetId=data[xx]['id'], range=data[xx]['range'],
            body=hh['clear_values_request_body']).execute()

        request = hh['service'].spreadsheets().values().update(
            spreadsheetId=data[xx]['id'], range=data[xx]['range'],
            valueInputOption=hh['value_input_option'][0], body=data[xx]['body']).execute()
