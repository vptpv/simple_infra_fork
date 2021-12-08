import os
import utils
from pprint import pprint

from configparser import ConfigParser
from cmdb import Infra
from keepass_db import KeePassDB
from spreadsheet import Sheet
from jira import Jira

config_name = 'config.ini'
config = ConfigParser()
check_config = config.read(config_name)
if not check_config:
    print(f"Не найден файл настроек {config_name}")
    exit(1)

assert 'cmdb' in config, 'В файле конфиге нет секции cmdb'
assert 'api_domain' in config['cmdb'], 'В файле конфига не указан api_domain'
assert 'standby' in config['cmdb'], 'В файле конфига не указан stanby адрес для апи'

# auth = slave_of_lamp.Authentication()

if not os.path.isdir('temp'):
     os.mkdir('temp')

kp = KeePassDB(config)
infra = Infra(config, None, None)
sh = Sheet()
jira = Jira()
infra.sheet = sh
infra.jira = jira
# def start():
#     if infra.check_access() != 200:
#         print('\n\tпеченьки протухли!\n')
#     infra.get_new_cookies()
#     user_data = infra.user_data
#     return user_data


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


def start():
    if infra.check_access() != 200:
        print('\n\tпеченьки протухли!\n')
        infra.get_new_cookies(kp)
    user_data = infra.user_data

    if user_data.get('UserName') != 's.savelov':
        infra.get_zip()
    else:
        for x in option:
            print(f"\t{x}")
        answer = input('\nответ: ').strip()
        if answer == '55':
            infra.get_zip()
        elif answer == '888':
            infra.change_network_roles(sh.read_infra())
        elif answer == '3':
            infra.add_sn(sh.read_infra())
        elif answer == '777':
            infra.change_mac_addresses(sh.read_infra())
        elif answer == '33':
            infra.sap_4_node()
        elif answer == '303':
            infra.vacant_sap_4_node()
        elif answer == '44':
            infra.sap_from_param(sh.read_infra(), 'name')
        elif answer == '404':
            infra.sap_from_param(sh.read_infra(), 'serial')
        elif answer == '101':
            infra.sn_from_sap(sh.read_infra())
        elif answer == '102':
            infra.host_from_sap(sh.read_infra())
        elif answer == '1':
            infra.remove_hosts_by_sap(sh.read_infra())
        elif answer == '11':
            infra.remove_hosts_by_name(sh.read_infra())
        elif answer == '2':
            infra.rename_hosts(sh.read_infra())
        elif answer == '202':
            infra.rename_sap(sh.read_infra())
        elif answer == 'make':
            infra.plan_test(sh.smart('accounting', 3))
        elif answer == '0make':
            infra.make_to_plan_node(sh.smart('accounting', 3))
        elif answer == '22':
            infra.set_sap_id(sh.read_infra())
        elif answer == 'жоско':
            infra.hard_add_sn(sh.read_infra())
        elif answer == 'get':
            print(utils.get_fat_name(str(input('\nимя ноды: ').strip())))
        elif answer == '_zip':
            # _zip()
            pass
        elif answer == 'read':
            pprint(sh.smart('accounting', 3))
        elif answer == 'base':
            sh.read_log()
        elif answer == 'jira':
            jira.hot_zip()
        elif answer == 'offi':
            infra.make_office_switch(sh.read_infra())
        elif answer == 'print':
            print(sh.read_another())
            # print(read.smart('temp','коммутаторы на продажу!A3:G10'))
            # print(read.infra())
            # print(read.smart('servers','Hot!A1:B'))
            # print(read.smart('test','servers!e2:E'))
            # print(read.smart('servers','another project!a2:E'))
        elif answer == '_Q':
            infra.get_zip_2()


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


if __name__ == '__main__':
    clear_console()
    print('привет, друг!\n\t\tпоработаем?\n')
    start()
