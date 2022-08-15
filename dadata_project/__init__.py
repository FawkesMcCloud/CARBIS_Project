# -*- encoding=utf-8 -*-
# This file was generated automatically
from loguru import logger

from dadata_project.dadataapi import DaDataAPI

from .appmenu import ApiCalls, AppMenuFactory

from .logusto import Logusto, LogConfig
from .aplication import App
from .config import Config
from .abc import BaseMenuStateMachine
from .win_userio import WindowsUserIO

__version__ = (1, 0, 0, 0)

logusto = Logusto(
    __name__,
    version_tuple=__version__,
    log_config=LogConfig(level=3, retention_days=3)
    )

def initConfig() -> Config:
    logger.info("Starting config init")
    try:
        config = Config()
    except (TypeError, ValueError) as e:
        logger.error("Invalid config %s", e)
    logger.success("Successfully initialized config")
    return config

def start():
    try:
        print("dadata_project v"+".".join(map(str, __version__)))
        with logusto.app_context(logger):
            config = initConfig()
            io = WindowsUserIO()
            App(
                config,
                BaseMenuStateMachine(
                    AppMenuFactory(
                        config,
                        ApiCalls(
                            config, 
                            DaDataAPI(config.general),
                            io
                        )
                    ).create_main_state(),
                    io
                )
            ).run()

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    start()
                