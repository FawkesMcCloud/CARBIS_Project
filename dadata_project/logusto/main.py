from contextlib import contextmanager
from datetime import datetime
import os, sys
from typing import ContextManager, Type

from .types import Toolchain
from .abc import LogConfig, IAppConfig

class Logusto:

    def __init__(
        self,
        appname: str,
        *,
        version_tuple: tuple = (0,0,0,0),
        app_config: IAppConfig = None,
        log_config: LogConfig = LogConfig(level=3, retention_days=7),
        dev_env: bool = False,
        toolchain_class: Type[Toolchain] = Toolchain
    ) -> None:
        self.appname = appname
        self.log_config = log_config
        self.app_config = app_config
        self.version_tuple = version_tuple
        self.dev_env = dev_env
        self.chains = list()
        self.toolchain_class = toolchain_class


    @contextmanager
    def get_toolchain(self, logger) -> ContextManager[Toolchain]:
        toolchain = self.toolchain_class(
            self.appname,
            self.version_tuple,
            self.app_config,
            self.log_config,
            logger
        )

        yield toolchain

        self.chains.append(toolchain)

    @property
    def current_filename(self) -> str:
        return datetime.now().strftime('%d-%m-%Y') + '.log'

    @property
    def current_logpath(self) -> str:
        return os.path.join(os.getcwd(), 'log', self.appname)

    @property
    def current_logfilepath(self) -> str:
        return os.path.join(self.current_logpath, self.current_filename)

    def handle(self, logger):
        logger.remove()

        if self.dev_env:
            with self.get_toolchain(logger) as toolchain:
                toolchain.assigned_logger = logger.add(
                    sys.stdout,
                    format=toolchain.formatter(),
                    filter=toolchain.filter(),
                    level='TRACE',
                    enqueue=True
                )

        with self.get_toolchain(logger) as toolchain:
            
            if os.path.exists(self.current_logpath):
                toolchain.retentor()(os.path.join(self.current_logpath, x) for x in os.listdir(self.current_logpath) if x != self.current_filename)
            
            logger.add(
                self.current_logfilepath,
                format=toolchain.formatter(),
                rotation=toolchain.rotator(),
                retention=toolchain.retentor(),
                compression=toolchain.compressor(),
                filter=toolchain.filter(),
                level='TRACE',
                enqueue=True
            )

        logger.critical('\\')

    @contextmanager
    def app_context(self, logger):
        self.handle(logger)

        yield None
        logger.critical('{text:*^70}'.format(text=" Штатное завершение работы "))
