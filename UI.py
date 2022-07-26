from Interface import Interface
import os
import json

cls = lambda: os.system('cls' if os.name == 'nt' else 'clear')


class UI:
    API = Interface()

    def __init__(self):
        self.main_loop()

    @staticmethod
    def print_options():
        print("1. Изменить токен")
        print("2. Изменить URL")
        print("3. Сменить язык EN\\RU")

        print("\n0. Выйти из меню настроек")

    @staticmethod
    def print_initial():
        print("Введите exit для выхода")
        print("Введите options для настроек")
        print("Введите адрес для поиска")

    def options_branch(self):
        while True:
            print(f"Текущие настройки:\n{self.API.config.show_config()}\n")

            self.print_options()
            cmd = input()
            if cmd == "1":
                cmd = input("Оставте поле пустым для отмены\nВведите новый токен:")
                if cmd != "":
                    self.API.config.change_token(cmd)
            elif cmd == "2":
                cmd = input("Оставте поле пустым для отмены\nВведите новый URL:")
                if cmd != "":
                    self.API.config.change_base_url(cmd)
            elif cmd == "3":
                self.API.config.change_language()
            elif cmd == "0":
                return False
            elif cmd == "exit":
                return True
            cls()

    def search_branch(self, addr):
        response = self.API.search(addr)

        code = response.status_code
        if code == 200:
            self.geo_branch(response)
        elif code == 400:
            print("Неверный запрос")
        elif code == 401 or code == 403:
            print("Неверный API ключ")
        elif code == 413:
            print("Слишком большая длина запроса")
        else:
            print("Непредвиденная ошибка")

        input("\nДля продолжения нажмите Enter...")

    def geo_branch(self, response):
        while True:
            suggestions = json.loads(response.content)["suggestions"]
            length = len(suggestions)
            for i, v in enumerate(suggestions):
                print(f"{i + 1}. {v['value']}")

            print("\n0. Назад\n")

            cmd = input("Выберите точный адрес из списка")
            try:
                cmd = int(cmd)
                if cmd == 0:
                    return True
                if 1 <= cmd <= length:
                    selected = suggestions[cmd - 1]
                    addr = selected['value']
                    lat = selected['data']['geo_lat']
                    lon = selected['data']['geo_lon']
                    print(f"Для адреса: {addr}\nШирота: {lat}\nДолгота: {lon}")
                    break
            except ValueError:
                print("Неправильно выбран вариант")
                cls()
        return False

    def main_loop(self):
        exit_flag = False
        while not exit_flag:
            self.print_initial()
            cmd = input()
            cmd = cmd.lower()
            cls()

            # напрямую не выходим из поиска
            if cmd == "exit":
                exit_flag = True
            elif cmd == "options":
                exit_flag = self.options_branch()
            else:
                self.search_branch(cmd)
