from dataclasses import dataclass
import os

from typing import Generator, List, NoReturn, Optional, Tuple
from datetime import datetime
from abc import ABC


@dataclass
class LogConfig:
    level: int
    retention_days: int

class IAppConfig(ABC):
    def as_str(self) -> str:
        ...


class IConfigurableLogger:
    def __init__(self, log_config: LogConfig = None) -> None:
        self.__config__ = log_config or LogConfig(5, 7)
        
    @property
    def log_config(self) -> LogConfig:
        return self.__config__

    @log_config.setter
    def log_config(self, value: LogConfig):
        self.__config__ = value


class IDepententWorker:
    
    def __init__(self, parent: 'IToolchain') -> None:
        self.__parent__ = parent

    @property
    def parent(self) -> 'IToolchain':
        return self.__parent__


class IFormatter(IDepententWorker):
    def format_time(self, date: datetime) -> str:
        ...

    def format_level(self, level: str) -> str:
        ...

    def format_source(self, record) -> str:
        ...

    def format_prefix(self, record) -> str:
        ...

    def format_message(self, prefix: str, record) -> str:
        ...

    def format(self, record) -> Generator[str, None, None]:
        ...

    def __call__(self, record) -> str:
        ...

class IRotator(IDepententWorker):

    def should_rotate(self) -> bool:
        ...

    def __call__(self, message, fileIO) -> bool:
        ...


class PathSplitter:

    def split_path(self, filepath) -> Tuple[str]:
        filename, fileext = os.path.splitext(os.path.basename(filepath))
        path = os.path.dirname(filepath)

        return (path, filename, fileext)

class IRetentor(IDepententWorker, PathSplitter):

    def __call__(self, some: List[str]) -> NoReturn:
        ...


class ICompressor(IDepententWorker, PathSplitter):

    def __call__(self, some: str) -> NoReturn:
        ...


class IFilter(IDepententWorker):

    def __call__(self, record) -> bool:
        ...
        

class IToolchain(IConfigurableLogger):
    
    def __init__(self, 
        appname:str,
        version_tuple: Tuple[int],
        app_config: IAppConfig,
        log_config: LogConfig = None,
        logger = None
    ) -> None:
        super().__init__(log_config)
        self.appname = appname
        self.app_config = app_config
        self.startup = True
        self.rotated = False
        self.version_tuple = version_tuple
        self.assigned_logger: Optional[int] = None
        self.logger = logger

        self.__formatter__ = self.formatter()
        self.formatter = lambda: self.__formatter__

        self.__rotator__ = self.rotator()
        self.rotator = lambda: self.__rotator__

        self.__retentor__ = self.retentor()
        self.retentor = lambda: self.__retentor__

        self.__compressor__ = self.compressor()
        self.compressor = lambda: self.__compressor__

        self.__filter__ = self.filter()
        self.filter = lambda: self.__filter__

    def formatter(self) -> IFormatter:
        ...

    def rotator(self) -> IRotator:
        ...

    def retentor(self) -> IRetentor:
        ...

    def compressor(self) -> ICompressor:
        ...

    def filter(self) -> IFilter:
        ...
    
    def levels_case(self, level:int) -> int:
        return {
            0: 50,
            1: 40,
            2: 30,
            3: 25,
            4: 25,
            5: 20,
            6: 20,
            7: 20,
            8: 10,
            9: 10,
            10: 5
        }.get(abs(level), 0)

    def level_names(self, severity: int) -> str:
        return {
            50: 'CRITICAL',
            40: 'ERROR',
            30: 'WARNING',
            25: 'SUCCESS',
            20: 'INFO',
            10: 'DEBUG',
            5: 'TRACE'
        }.get(severity, 'TRACE')