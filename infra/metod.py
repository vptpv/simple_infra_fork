import requests, json

def get_fat_name(auth, host):
    host = hostname(host)
    rackname = f" and DataCenterRackName eq '{host[-6:-2]}'"
    select = 'DataCenterLocation,DataCenterName'
    filter_ = f"DataCenterRackName eq '{host[-6:-2]}'"
    url = f"{auth.api_domain}/api/hosts?$top=1&$select={select}&$filter={filter_}"
    r = requests.get(url, cookies=auth.cookies)
    json_1 = json.loads(r.text)
    for x in json_1:
        if x.get('DataCenterLocation') is not None:
            string = fat_name(host, x.get('DataCenterName'))
            return string

def fat_name(host, rack_group):
    bzh = '000'+str(int(host[-3:])+first_unit(host, rack_group))
    hostname = f"FT{host[-6:-3]}{bzh[-3:]}"
    return hostname

def hostname(host): # добавляет префикс хосту
    if len(host) > 5:
        if host[-6]=='5' or host[-6]=='6':
            return 'eva' + host[-6:]
        elif host[-6]=='2':
            return 'cvt' + host[-6:]
        elif host[-6]=='8':
            return 'sdn' + host[-6:]
        else:
            return host
    else:
        return host

def position(host, rack_group): # определяет позицию в стойке
    return int(host[-2:]) + first_unit(host, rack_group)

def first_unit(host, rack_group): # определяет позицию в стойке
    rack_group = str(rack_group).lower()
    if rack_group[0:5] == 'icva2':
        if host[-6:-2] == '6129':# стойка с квм переключателем
            if int(host[-2:]) > 10:
                return 9
            else:
                return 8
        else:
            return 8
    elif rack_group[0:5] == 'icva3':
        return 9
    elif rack_group[0:5] == 'icva1':
        if host[-6:-2] == '5360' or host[-6:-2] == '5280' or host[-6:-2] == '5040' or host[-6:-2] == '5160':#стойки хостинга
            return 13
        elif rack_group[-3:] == '_00' or rack_group[-3:] == '_11':
            return 9
        else:
            return 7
    elif rack_group[0:5] == 'icva_':
        if host[-6:-2] == '5980' or host[-6:-2] == '5981' or host[-6:-2] == '5982':#стойки лабы
            return 1
