import threading
import PySimpleGUI as sg

from enum import Enum
from dadata_project import userio
from .abc import BaseUserIO , BaseMenuState
from .userio import Action


class WindowBridge:
    def __init__(self):
        self.action = None


class UserWindow(threading.Thread):
    def __init__(self, bridge: WindowBridge):
        super().__init__()

        sg.theme('DarkAmber')
        layout = [ [ sg.Text('loading...') ] ]
        self.current_state = None
        self.window = sg.Window('DaData project', layout)

        self.bridge = bridge

    def run(self):
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
                break

            for i, item in enumerate(self.current_state.items):
                if item.text == event:
                    self.current_state.cur_idx = i
                    self.bridge.action = Action.ENTER

        self.window.close()

    def update(self, state: BaseMenuState):
        if self.current_state == state:
            return
        else:
            self.current_state = state
        
        layout = [ [ sg.Text(state.header) ] ]
        for item in state.items:
            layout.append( [ sg.Button(item.text) ] )
        # self.window.Rows.clear()
        # self.window.add_rows(layout)
        self.window.close()
        self.window = sg.Window('DaData project', layout)
        pass


class WindowsUserIO(BaseUserIO):
    def __init__(self):
        self.bridge = WindowBridge()
        self.user_window = UserWindow(self.bridge)
        self.user_window.start()
        
    def render_state(self, state:BaseMenuState) -> None:
        self.user_window.update(state)
        pass
        # raise NotImplemented()

    def get_action(self) -> Enum:
        if self.user_window.isAlive() == False:
            exit(0)
        elif self.bridge.action is not None:
            result_act = self.bridge.action
            self.bridge.action = None
            return result_act

    def get_line(self, promt:str) -> str:
        pass
        # raise NotImplemented()