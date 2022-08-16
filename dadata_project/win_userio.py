from asyncore import read
import threading
import PySimpleGUI as sg

from enum import Enum
from dadata_project import userio
from .abc import BaseUserIO , BaseMenuState
from .userio import Action


class WindowBridge:
    def __init__(self):
        self.action = None
        self.th_lock = threading.Lock()
        self.reader_value = None


class WinTypes:
    MENU = 'menu'
    TEXTREADER = 'text_reader'


class WinResult:
    EXIT = -1
    NOTHING = 0
    CHANGESTATE = 1


class UserWindow(threading.Thread):
    def __init__(self, bridge: WindowBridge):
        super().__init__()

        sg.theme('DarkAmber')
        layout = [ [ sg.Text('loading...') ] ]
        self.current_state = None
        self.window = sg.Window('DaData project', layout)

        self.bridge = bridge
        self.win_type = None

    def run(self):
        while True:
            with self.bridge.th_lock:
                r = self.read_action()
                if r == WinResult.EXIT:
                    break
                elif r == WinResult.CHANGESTATE:
                    self.window.close()
                    self.bridge.th_lock.acquire()
        self.window.close()

    def read_action(self) -> WinResult:
        self.window.refresh()
        if self.win_type == WinTypes.MENU:
            return self.read_menu_action()
        elif self.win_type == WinTypes.TEXTREADER:
            return self.read_string_reader_action()

    def read_menu_action(self) -> WinResult:
        event, values = self.window.read()
        if event == sg.WIN_CLOSED or event == 'Выход':
            return WinResult.EXIT
        for i, item in enumerate(self.current_state.items):
            if item.text == event:
                self.current_state.cur_idx = i
                self.bridge.action = Action.ENTER
        return WinResult.CHANGESTATE

    def read_string_reader_action(self) -> WinResult:
        event, values = self.window.read()
        if event == sg.WIN_CLOSED or event == 'Применить':
            self.bridge.reader_value = values[0]
            return WinResult.CHANGESTATE
        else:
            return WinResult.NOTHING

    def set_menu_state(self, state: BaseMenuState):
        if self.current_state == state and self.win_type == WinTypes.MENU:
            return
        else:
            self.current_state = state
        
        layout = [ [ sg.Text(state.header) ] ]
        for item in state.items:
            layout.append( [ sg.Button(item.text) ] )
        self.window = sg.Window('DaData project', layout)
        self.win_type = WinTypes.MENU
        self.bridge.th_lock.release()

    def set_to_string_reader(self, promt: str):
        layout = [ 
            [ sg.Text(promt), sg.InputText() ],
            [ sg.Button('Применить') ]
        ]
        self.window = sg.Window('Изменение настройки', layout)
        self.win_type = WinTypes.TEXTREADER
        self.bridge.th_lock.release()


class WindowsUserIO(BaseUserIO):
    def __init__(self, bridge: WindowBridge, user_window: UserWindow):
        self.bridge = bridge
        self.user_window = user_window
        self.bridge.th_lock.acquire()
        self.user_window.start()
        
    def render_state(self, state:BaseMenuState) -> None:
        self.user_window.set_menu_state(state)

    def get_action(self) -> Enum:
        if self.user_window.isAlive() == False:
            exit(0)
        elif self.bridge.action is not None:
            result_act = self.bridge.action
            self.bridge.action = None
            return result_act

    def get_line(self, promt:str) -> str:
        self.user_window.set_to_string_reader(promt)
        while self.bridge.reader_value == None:
            pass
        val = self.bridge.reader_value
        self.bridge.reader_value = None
        return val
