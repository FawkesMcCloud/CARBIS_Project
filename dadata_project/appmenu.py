from typing import Callable, Iterable
from loguru import logger

from .dadataapi import DaDataAPI, DaDataException
from .sugengine import Suggestion
from .config import Config, Language
from .abc import BaseMenuState, BaseMenuStateMachine, BaseStateFactory, MenuItem
from .userio import Action, ConsoleUserIO


class AppMenuState(BaseMenuState):
    def perform_action(self, action:Action):
        logger.success(f"Got action{action}")
        if action == Action.UP:
            if self.cur_idx - 1 < 0:
                self.cur_idx = 0
            else:
                self.cur_idx -= 1
        elif action == Action.DOWN:
            if self.cur_idx + 1 >= len(self.items):
                self.cur_idx = len(self.items) - 1
            else:
                self.cur_idx += 1
        elif action == Action.ENTER:
            self.items[self.cur_idx].action(self._context, self)


class ApiCalls():
    def __init__(self, config:Config, api:DaDataAPI, io:ConsoleUserIO) -> None:
        self.api = api
        self.config = config
        self.io = io


    def get_suggestions(self) -> Iterable[Suggestion]:
        query = self.io.get_line("Введите адрес в произвольном формате\n>")
        return self.api.get_suggestions(query)


    def get_coords(self, suggestion:Suggestion):
        return self.api.get_coordinates(suggestion)

    def change_token(self,s:BaseMenuState):
        token = self.io.get_line("Новый токен:")
        self.config.update({'general': {'api_token': token}})
        s.header = self.config.general

    def change_url(self, s:BaseMenuState):
        url = self.io.get_line("Новый URL:")
        self.config.update({'general': {'base_url': url}})
        s.header = self.config.general

    def change_language(self, m:BaseMenuStateMachine, s:BaseMenuState, language:Language):
        self.config.update({'general': {'language' : language}})
        s.prev_state.header = str(self.config.general)
        m.change_state(s.prev_state)
         

        
    

class AppMenuFactory(BaseStateFactory):
    def __init__(self, config:Config, functions:ApiCalls) -> None:
        self.config = config
        self.calls = functions

    def create_suggestion_lambda(self, suggestion:Suggestion) -> Callable[[BaseMenuStateMachine,BaseMenuState], None]:
        return lambda m,_: m.change_state(self.create_info_state(f"{suggestion.addr}\n{self.calls.get_coords(suggestion)}"))


    def create_state(self, menu_items:Iterable[MenuItem], header:str = "", prev_state:'BaseMenuState' = None) -> BaseMenuState:
        return AppMenuState(menu_items, header, prev_state)

    def create_exit_item(self, text:str = "Назад") -> MenuItem:
        return MenuItem(text, lambda m,s: m.change_state(s.prev_state))

    def create_main_state(self) -> BaseMenuState:
        menu_items = [
            MenuItem("Выполнить запрос", lambda m,_: m.change_state(self.create_suggestions_state())),
            MenuItem("Настройки", lambda m,_: m.change_state(self.create_settings_state())),
            self.create_exit_item("Выход")
        ]
        return self.create_state(menu_items, "Главное меню", None)

    def create_settings_state(self) -> BaseMenuState:
        menu_items = [
            MenuItem("Сменить токен", lambda _,s: self.calls.change_token(s)),
            MenuItem("Сменить URL", lambda _,s:self.calls.change_url(s)),
            MenuItem("Сменить язык", lambda m,_:m.change_state(self.create_change_lang_state())),
            self.create_exit_item()
        ]
        header = f"Текущие настройки:\n{self.config.general}"
        return self.create_state(menu_items, header, self.create_main_state())

    def create_change_lang_state(self) -> BaseMenuStateMachine:
        menu_items = [
            MenuItem("Русский", lambda m,s: self.calls.change_language(m,s, Language.Russian)),
            MenuItem("Английский", lambda m,s: self.calls.change_language(m,s, Language.English)),
        ]
        return self.create_state(menu_items, f"текущий язык:{self.config.general.language.name}", self.create_settings_state())

    def create_suggestions_state(self) -> BaseMenuState:
        try:
            suggestions = self.calls.get_suggestions()
            menu_items = [
                MenuItem(
                    i.addr,
                    self.create_suggestion_lambda(i)
                ) for i in suggestions
            ]
            menu_items.append(MenuItem("Назад", lambda m,_: m.change_state(self.create_main_state())))
            return self.create_state(menu_items, "Выберите адрес для уточнениня координат")
        except DaDataException:
            text = "Возникла ошибка при работе с api DaData\n"
            text += "Проверте токен и URL в настройках\n"
            text += "Проверте есть ли соеденение с интернетом"
            return self.create_info_state(text)


    def create_info_state(self, message:str) -> BaseMenuState:
        menu_items = [self.create_exit_item()]
        return self.create_state(menu_items, message, self.create_main_state())

    