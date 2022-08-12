from loguru import logger
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable

#region MenuStateMachine
@dataclass
class MenuItem():
    text: str
    action: Callable[['BaseMenuStateMachine','BaseMenuState'], None]


class BaseMenuState():
    def __init__(self, menu_items:Iterable[MenuItem], header:str = "", prev_state:'BaseMenuState' = None) -> None:
        self._context:'BaseMenuStateMachine' = None
        self.prev_state = prev_state

        self.header = header

        self.items = menu_items
        self.cur_idx = 0


    def perform_action(self, action:Enum):
        raise NotImplemented()


class BaseMenuStateMachine():
    def __init__(self, init_state:BaseMenuState, io:'BaseUserIO') -> None:
        self.io = io
        self.state = None
        self.change_state(init_state)

    def change_state(self, new_state:BaseMenuState) -> None:
        self._state = new_state
        if not self.is_none_state():
            self._state._context:'BaseMenuState' = self
        logger.success(f"Changed state to {self._state}")

    def handle_state(self):
        self.io.render_state(self._state)
        action = self.io.get_action()
        self._state.perform_action(action)

    def is_none_state(self):
        return self._state is None

#region Factory
class BaseStateFactory():
    def create_state(self, menu_items:Iterable[MenuItem], header:str = "", prev_state:'BaseMenuState' = None) -> BaseMenuState:
        raise NotImplemented()

#endregion 

#endregion    


#region BaseUserIO
class BaseUserIO():
    def render_state(self, state:BaseMenuState) -> None:
        raise NotImplemented()

    def get_action(self) -> Enum:
        raise NotImplemented()

    def get_line(self, promt:str) -> str:
        raise NotImplemented()
#endregion