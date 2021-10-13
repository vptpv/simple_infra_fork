import json, platform
import slave_of_lamp, new_fu
from pprint import pprint
from sheets import read, write
from infra import delete, metod, get, kick, make
from jira_ import j_read

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
        '  102. получить имя по метке',
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
        ' base. читаем базу',
        ' jira. читаем таски на горячий зип',
    ]

def dict_reader():
    user_data = start()
    if user_data.get('UserName') != 's.savelov':
        get.zip(auth)
    else:
        for x in option:
            print(f"\t{x}")
        answer = input('\nответ: ').strip()
        get.zip(auth)                                                       if answer ==    '55' else ''
        kick.change_network_roles(auth, read.infra())                       if answer ==   '888' else ''
        kick.add_sn(auth, read.infra())                                     if answer ==     '3' else ''
        kick.change_mac_addresses(auth, read.infra())                       if answer ==   '777' else ''
        get.sap_4_node(auth)                                                if answer ==    '33' else ''
        get.vacant_sap_4_node(auth)                                         if answer ==   '303' else ''
        get.sap_from_param(auth, read.infra(), 'name')                      if answer ==    '44' else ''
        get.sap_from_param(auth, read.infra(), 'serial')                    if answer ==   '404' else ''
        get.sn_from_sap(auth, read.infra())                                 if answer ==   '101' else ''
        get.host_from_sap(auth, read.infra())                               if answer ==   '102' else ''
        delete.hosts_by_sap(auth, read.infra())                             if answer ==     '1' else ''
        delete.hosts_by_name(auth, read.infra())                            if answer ==    '11' else ''
        kick.rename_hosts(auth, read.infra())                               if answer ==     '2' else ''
        kick.rename_sap(auth, read.infra())                                 if answer ==   '202' else ''
        make.switch(auth,read.infra())                                      if answer ==  'make' else ''
        make.terminal(auth,read.infra())                                    if answer == 'make2' else ''
        make.dwdm(auth,read.infra())                                        if answer == 'make3' else ''
        make.to_plan_node(auth, read.infra())                               if answer == '0make' else ''
        kick.set_sap_id(auth, read.infra())                                 if answer ==    '22' else ''
        kick.hard_add_sn(auth, read.infra())                                if answer == 'жоско' else ''
        print(metod.get_fat_name(auth, str(input('\nимя ноды: ').strip()))) if answer ==   'get' else ''
        _zip()                                                              if answer ==  '_zip' else ''
        pprint(read.install())                                              if answer ==  'read' else ''
        new_fu.read_log()                                                   if answer ==  'base' else ''
        j_read.hot_zip()                                                    if answer ==  'jira' else ''

def _zip():
    values = read._zip()
    write._zip(values)

if __name__ == '__main__':
    if platform.system() != 'Windows':
        print(chr(27) + "[2J")
    print('привет, друг!\n\t\tпоработаем?\n')
    dict_reader()