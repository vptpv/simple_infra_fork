import getpass
import os
import platform
import re
import json
from pathlib import Path
from uuid import UUID

from pykeepass import PyKeePass
from pykeepass.exceptions import CredentialsError

#from mainer import config


class KeePassDB:
    def _find_db(self):
        search_path = input(
            "\nВведите путь для поиска базы KeePass. Нажмите Enter чтобы искать в домашнем каталоге: ").strip()
        print(search_path)
        if search_path:
            home_path = search_path
        else:
            home_path = {
                'Linux': '~/',
                'Darwin': '~/',
                'Windows': f"C:\\Users\\{getpass.getuser()}\\"  # спасибо Хику за это
            }[platform.system()]

        print('\n\tищу базу данных...')
        result = [str(x) for x in Path(os.path.expanduser(home_path)).rglob("*.kdbx")]

        list_h = dict(enumerate(result))
        if len(list_h) == 1:
            self.db_path = list_h[0]  # если база одна
            print(f"выбрана база:\n\t{self.db_path}")
        elif len(list_h.keys()) > 1:  # если баз нашлось больше чем одна
            print(f"нашлось несколько баз:")
            for i in list_h.keys():
                print(f"\t{i} - {list_h[i]}")
            self.db_path = list_h[int(input('\nвведи номер базы из списка: ').strip())]
            print(f"выбрана база:\n\t{self.db_path}. Сохраняем в конфиг")
            self.config.set('keepassx', 'path', self.db_path)
            self.config.write(open('config.ini', 'w'))
        else:  # если ничего не нашлось
            _ = input(
                '\n\tу вас должна быть создана база данных с паролями *.kdbx\n\tиначе ничего не получится\n\t').strip()
            # print(f"выбрана:\n\t{db_path}")
            exit(1)

    def __init__(self, config):
        self.config = config
        self.db_path = self.config['keepassx'].get('path', None)
        print(self.db_path)
        if not self.db_path:
            self._find_db()
        attempt = 5
        kp = None
        while attempt:
            try:
                kp = PyKeePass(os.path.expanduser(self.db_path), password=getpass.getpass(prompt='\n\tпароль от БД:'))
            except FileNotFoundError:
                self._find_db()
            except CredentialsError:
                print("Неверный пароль к БД KeePass!")
            if kp:
                break
            attempt -= 1
        else:
            print("Попытки исчерпаны, запускай заново")
            exit(1)
        kp_entry = kp.find_entries(url='ra.ma*', regex=True, first=True)
        if re.match(r"{REF:[UP]@I:", kp_entry.username):
            ref_entry = kp.find_entries(uuid=UUID(re.match(r'{REF:[PU]@I:(.*)}', kp_entry.username)[1]), first=True)
            kp_entry.password = ref_entry.password
            kp_entry.username = ref_entry.username
        self.entry = kp_entry
        assert kp_entry.attachments, 'В записи KeePass должны быть аттачи, см. конфлюенс'
        entry_attachments = {x.filename: x.data for x in self.entry.attachments}
        self.credentials = json.loads(entry_attachments.get('credentials.json', None))
        self.jira_bot = json.loads(entry_attachments.get('jira_bot.json', None))
        assert self.credentials, 'не хватает файлика\n\n\tнайди credentials.json в конфлюенсе'
        assert self.entry.notes, 'вместо заметки шляпа'
        assert self.jira_bot, 'не хватает файлика\n\n\tнайди jira_bot.json в конфлюенсе'

    def make_payload(self):
        token_field = self.config['keepassx'].get('token_field', '')
        token = self.entry.custom_properties.get(token_field, None)
        if not token:
            if not self.entry.custom_properties:
                print("\n\tСоздайте поле с токеном в записи KeePass")
                exit(1)
            print("Сейчас сохранены эти поля, выберите из них токен")
            custom_fields = list(enumerate(self.entry.custom_properties.keys(), start=1))
            for item in custom_fields:
                print(f"{item[0]} - {item[1]}")
            print("0 - Выход")
            field_number = input('\nвыбери из списка: ').strip()
            while not field_number.isdigit():
                print("Не смешно, попробуй ещё раз\n")
                field_number = input('\nвыбери из списка: ').strip()
                exit(1)
            if not int(field_number):
                print("Выход")
                exit(1)

            selected_field = custom_fields[int(field_number)-1][1]
            # print(field_number, custom_fields, selected_field)
            self.config.set('keepassx', 'token_field', selected_field)
            self.config.write(open('config.ini', 'w'))
            token = self.entry.custom_properties.get(selected_field, 0)
        input_otp = input('\n\tцифры с ОТП: ')
        otp_password = f"{token}{input_otp.strip()}"
        payload = {
            "Name": self.entry.username,
            "DomainPassword": self.entry.password,
            "OtpPassword": otp_password
        }
        return payload
