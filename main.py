import json, os
import slave_of_lamp
from pprint import pprint
from sheets import read, write
from infra import delete, metod, get, kick, make

auth = slave_of_lamp.authentication()

def start():
    if auth.check_access() != 200:
        print('\n\tпеченьки протухли!\n')
        auth.get_new_cookies()
    user_data = auth.user_data
    return user_data

option = [
        '   55. получи остатки get.zip()',
        '  888. изменить роль свитчу change_network_roles()',
        '    3. добавить серийник add_sn()',
        '  777. добавить мак change_mac_addresses()',
        '   33. получить наклейки для толстяков get.sap_4_node()',
        '  303. получить свободные наклейки для нод get.vacant_sap_4_node()',
        '   44. получи сапметки по именам line(new_name)',
        '  404. получи сапметки по серийникам line(serial)',
        '  101. получить серийник по метке',
        '    1. удалить хосты по меткам',
        '   11. удалить хосты по именам',
        '    2. переименовать хосты по именам',
        '  202. переименовать хосты по меткам',
        ' make. спланировать хосты switch()',
        '0make. спланировать ноды в пустые шасси to_plan_node(reader)',
        '   22. присвоить метки set_sap_id(reader)',
        'жоско. добавить серийник жоско',
        '  get. получить имя фата',
        ' _zip. учесть расходы из учёта',
        ' read. читаем список на планирование',
    ]

def dict_reader():
    user_data = start()
    if user_data.get('UserName') != 's.savelov':
        get.zip(auth)
    else:
        for x in option:
            print(f"\t{x}")
        answer = input('\nответ: ').strip()
        if answer == '55':
            get.zip(auth)
        elif answer == '888':
            kick.change_network_roles(auth, read.infra())
        elif answer == '3':
            kick.add_sn(auth, read.infra())
        elif answer == '777':
            kick.change_mac_addresses(auth, read.infra())
        elif answer == '33':
            get.sap_4_node(auth)
        elif answer == '303':
            get.vacant_sap_4_node(auth)
        elif answer == '44':
            get.sap_from_param(auth, read.infra(), 'name')
        elif answer == '404':
            get.sap_from_param(auth, read.infra(), 'serial')
        elif answer == '101':
            get.sn_from_sap(auth, read.infra())
        elif answer == '1':
            delete.hosts_by_sap(auth, read.infra())
        elif answer == '11':
            delete.hosts_by_name(auth, read.infra())
        elif answer == '2':
            kick.rename_hosts(auth, read.infra())
        elif answer == '202':
            kick.rename_sap(auth, read.infra())
        elif answer == 'make':
            make.switch(auth,read.infra())
        elif answer == 'make2':
            make.terminal(auth,read.infra())
        elif answer == 'make3':
            make.dwdm(auth,read.infra())
        elif answer == '0make':
            make.to_plan_node(auth, read.infra())
        elif answer == '22':
            kick.set_sap_id(auth, read.infra())
        elif answer == 'жоско':
            kick.hard_add_sn(auth, read.infra())
        elif answer == 'get':
            print(metod.get_fat_name(auth, str(input('\nимя ноды: ').strip())))
        elif answer == '_zip':
            _zip()
        elif answer == 'read':
            pprint(read.install())

def _zip():
    values = read._zip()
    write._zip(values)

if __name__ == '__main__':
    print(chr(27) + "[2J")
    print('привет, друг!\n\t\tпоработаем?')
    dict_reader()