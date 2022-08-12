from enum import Enum
import os
from msvcrt import getch

from .abc import BaseUserIO , BaseMenuState

class Action(Enum):
    UP = 3
    DOWN = 4
    ENTER = 1
    BACK = 0
    UNDEFINED = -1

#KEYCODES
KEY_UP = 72
KEY_DOWN = 80
KEY_SPECIAL = 224
KEY_ENTER = 13
KEY_ESC = 27


class ConsoleUserIO(BaseUserIO):
    def clear(self):
        os.system("cls")
    
    def render_state(self, state: BaseMenuState) -> None:
        self.clear()
        print(self.format_state(state))
    
    def format_state(self, state:BaseMenuState) -> str:
        text = ""
        if state.header != "":
            text += f'{state.header}\n\n'
        for i, item in enumerate(state.items):
            text += f"{'>' if i == state.cur_idx else ' '}{item.text}\n"
        return text

    def get_action(self) -> Action:
        key = ord(getch())

        if key == KEY_SPECIAL:
            key = ord(getch())
            if key == KEY_UP:
                return Action.UP
            elif key == KEY_DOWN:
                return Action.DOWN

        elif key == KEY_ENTER:
            return Action.ENTER
        elif key == KEY_ESC:
            return Action.BACK
        return Action.UNDEFINED

    def get_line(self, promt:str = "") -> str:
        self.clear()
        return input(promt)

        

