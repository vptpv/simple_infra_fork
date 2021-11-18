import json, platform
import slave_of_lamp, new_fu
from pprint import pprint
from sheets import read, write
from infra import delete, metod, get, kick, make, to_plan, variable
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
        ' make. спланировать хосты !!!может работать не корректно!!!',
        '0make. спланировать ноды в пустые шасси to_plan_node(reader)',
        '   22. присвоить метки set_sap_id(reader)',
        'жоско. добавить серийник жоско',
        '  get. получить имя фата',
        # ' _zip. учесть расходы из учёта',
        ' read. читаем список на планирование',
        ' base. читаем базу',
        ' jira. читаем таски на горячий зип',
        ' offi. спланировать хосты office_switch()',
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
        to_plan.test(auth,read.smart('accounting',3))                       if answer ==  'make' else ''
        make.to_plan_node(auth,read.smart('accounting',3))                  if answer == '0make' else ''
        kick.set_sap_id(auth, read.infra())                                 if answer ==    '22' else ''
        kick.hard_add_sn(auth, read.infra())                                if answer == 'жоско' else ''
        print(metod.get_fat_name(str(input('\nимя ноды: ').strip())))       if answer ==   'get' else ''
        # _zip()                                                              if answer ==  '_zip' else ''
        pprint(read.smart('accounting',3))                                  if answer ==  'read' else ''
        new_fu.read_log()                                                   if answer ==  'base' else ''
        j_read.hot_zip()                                                    if answer ==  'jira' else ''
        make.office_switch(auth,read.infra())                               if answer ==  'offi' else ''
        if answer == 'print':
            print(read.another())
            print(read.smart('temp','коммутаторы на продажу!A3:G10'))
            print(read.infra())
            print(read.smart('servers','Hot!A1:B'))
        variable.get_zip_2(auth)                                            if answer ==    '_Q' else ''

def _zip():
    values = read._zip()
    write._zip(values)

if __name__ == '__main__':
    if platform.system() != 'Windows':
        print(chr(27) + "[2J")
    print('привет, друг!\n\t\tпоработаем?\n')
    dict_reader()
