import threading

from enum import Enum
from dadata_project import userio
from .abc import BaseUserIO , BaseMenuState
from .userio import Action

from pyforms.basewidget import BaseWidget
from pyforms import start_app
from pyforms.controls import ControlButton, ControlLabel


class Window(BaseWidget):
    def __init__(self):
        super().__init__('DaData project')
        self._buttons = []
        print('constr')
        self._button = ControlButton('Кнопочка')
        self._button.value = self.button_action
        
        # if WindowBridge.menu_state is not None:
        #     self.draw_interface(WindowBridge.menu_state)
        #     WindowBridge.menu_state = None

    def draw_interface(self, menu_state: BaseMenuState):
        self._label = ControlLabel(menu_state.header)
        self._buttons.clear()
        for item in menu_state.items:
            button = ControlButton(item.text)
            button.value = item.action
            self._buttons.append(button)
        self._button = button
        print(self._button)
        

    def button_action(self):
        WindowBridge.action = Action.BACK
        self._button2 = ControlButton('Новая кнопочка')
        self.__init__()
        
        


class WindowThread(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        start_app(Window)


class WindowBridge:
    action = Action.UNDEFINED
    menu_state = None


class WindowsUserIO(BaseUserIO):
    def __init__(self):
        self.thread = WindowThread()
        self.thread.start()
        
    def render_state(self, state:BaseMenuState) -> None:
        WindowBridge.menu_state = state
        # raise NotImplemented()

    def get_action(self) -> Enum:
        if self.thread.isAlive() == False:
            exit(0)
        elif WindowBridge.action != Action.UNDEFINED:
            result_act = WindowBridge.action
            WindowBridge.action = Action.UNDEFINED
            return result_act

    def get_line(self, promt:str) -> str:
        pass
        # raise NotImplemented()