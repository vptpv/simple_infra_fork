import requests, json

def get_fat_name(host):
    host = hostname(host)
    r_group = rack_group(host[-6:-3])
    if r_group[:4].lower() == 'icva':
        poz = position(host, r_group)
        per = float(host[-2:])/4
        bzh = '000'+str(poz-int((per-int(per))/0.25))
        return f"FT{host[-6:-2]}{bzh[-2:]}"
    else:
        # bzh = '000'+str(int(int(host[-2:])/4)+first_unit(host, rack_group))
        return 'fatname'

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

def rack_group(row):
    number_ = int(int(row[-2:])/4)
    if row[0] == '5':
        first = 'ICVA1_'; second = f"0{number_}"[-2:]
    elif row[0] == '6' and number_ <= 4:
        first = 'ICVA2_'; second = str(number_)
    elif row[0] == '6' and number_ > 4:
        first = 'ICVA3_'
        number_ = int(number_ - 4); second = str(number_)
    return first + second

def get_location(host, host_type):
    if host_type == 'Network':
        rack = host.split('-')[2].upper()
    else:
        rack = host[-6:-2]
    row = rack[:-1]
    group = rack_group(row)
    return [group[:4],group,row,rack]
