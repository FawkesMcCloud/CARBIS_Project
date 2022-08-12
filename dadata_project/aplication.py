from .config import Config
from .abc import BaseMenuStateMachine

class App():
    def __init__(self, config:Config, state_machine:BaseMenuStateMachine) -> None:
        self.config = config
        self.sm = state_machine

    def run(self):
        while(not self.sm.is_none_state()):
            self.sm.handle_state()
