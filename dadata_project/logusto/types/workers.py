from datetime import date, datetime, timedelta
from io import TextIOWrapper
import json
import os
from typing import Generator, List, NoReturn
import traceback
from zipfile import ZipFile, ZIP_DEFLATED
# from loguru import Record

from ..abc import ICompressor, IFilter, IRetentor, IToolchain, IFormatter, IRotator, LogConfig, IAppConfig


class Formatter(IFormatter):

    fmt = '{time} [{level:<8}]'
    LINE_LEN = 70
    TEXT_LEN = LINE_LEN - 4

    def format_time(self, date: datetime) -> str:
        tz = date.tzinfo.utcoffset(None)
        s = tz.seconds
        hours, remainder = divmod(s, 3600)
        minutes = remainder // 60
        return f'{date.hour:>02}:{date.minute:>02}:{date.second:>02}.{date.microsecond // 1000:>03}+{hours:>02}:{minutes:>02}'

    def format_level(self, level: str) -> str:
        return f'[{level:<8}]'

    def format_source(self, record: dict) -> str:
        return f"{record['name']}:{record['function']}({record['line']})"

    def format_prefix(self, record: dict) -> str:
        return f"{self.format_time(record['time'])} {self.format_level(record['level'].name)} " + (f"{self.format_source(record)} | " if self.parent.log_config.level >= 6 else '')

    def format_message(self, prefix: str, record: dict) -> Generator[str, None, None]:
        lines = record['message'].splitlines(False)

        if record['exception']:
            e = record['exception']
            if self.parent.log_config.level >= 10:
                try:
                    import stackprinter
                except ImportError:
                    lines.extend(
                        traceback.format_exception(
                            etype=e.type,
                            value=e.value,
                            tb=e.traceback
                        )
                    )
                else:
                    lines.append( stackprinter.format(e) )
            elif self.parent.log_config.level >= 8:
                lines.extend( traceback.format_exception(
                            etype=e.type,
                            value=e.value,
                            tb=e.traceback
                        ) )
            else:
                lines[0] += f': ({e.type.__name__}) {e.value}'

        
        
        if len(lines) == 1:
            yield f'{prefix}{lines[0]}\n'
        else:
            yield f'{prefix} \\\n\n'
            
            for line in lines:
                yield line.lstrip("\n\r")+'\n'

            yield '\n'

    def format(self, record: dict) -> Generator[str, None, None]:
        prefix = self.format_prefix(record)

        yield from self.format_message(prefix, record)


    def format_header_string(self, text):
        fmt = f'* {{text:<{self.TEXT_LEN}}} *\n'
        
        line = ''
        while len(text) > self.TEXT_LEN:
            line += fmt.format(text=text[:self.TEXT_LEN]) 
            text = text[self.TEXT_LEN:]
        line += fmt.format(text=text)

        return line

    def get_header_string(self, text:str):
        if text == '':
            return self.format_header_string(' ')
        else:
            return ''.join(self.format_header_string(line) for line in text.splitlines(False))

    def format_header(self, version_tuple, app_config: IAppConfig):
        data = ''
        if self.parent.rotated:
            data += '{text:=^{line_len}}\n'.format(line_len=self.LINE_LEN, text=" <-- CUT --> ")
        else:
            data += '\n' + '*'*self.LINE_LEN + '\n'
        data += self.get_header_string('')
        data += self.get_header_string(('Запуск ' if self.parent.startup else '' )+ self.parent.appname + ' v'+'.'.join(str(x) for x in version_tuple))
        data += self.get_header_string('Системное время: ' + datetime.now().isoformat())
        data += self.get_header_string('Путь на диске: ' + os.getcwd())
        data += self.get_header_string(f'Уровень логирования: {self.parent.level_names( self.parent.levels_case(self.parent.log_config.level) )} ({self.parent.log_config.level})')
        data += self.get_header_string(f'Срок хранения журнала: {self.parent.log_config.retention_days} дней')

        data += self.get_header_string('')
        if not app_config:
            data += self.get_header_string('Данные о конфигурации приложения не подлежат отображению.')
        else:
            data += self.get_header_string('Текущая конфигурация приложения:\n\n'+app_config.as_str())

        data += self.get_header_string('')
        data += '*'*self.LINE_LEN + '\n'
        self.parent.rotated = False
        self.parent.startup = False
        return data

    def __call__(self, record) -> str:
        record['extra']['serialized'] = ''

        if self.parent.rotated or self.parent.startup:
            record['extra']['serialized'] = self.format_header(self.parent.version_tuple, self.parent.app_config)
        
        record['extra']['serialized'] += ''.join(x for x in self.format(record))
        
        return '{extra[serialized]}'


class Rotator(IRotator):
    
    def __init__(self, parent: 'IToolchain') -> None:
        super().__init__(parent)
        self.rotate_date = self.calc_rotation_date()

    def calc_rotation_date(self) -> datetime:
        now = datetime.now() + timedelta(days=1)
        return now.replace(hour=0, minute=0, second=0, microsecond=0)


    def should_rotate(self) -> bool:
        return datetime.now() > self.rotate_date
    
    def __call__(self, message, fileIO: TextIOWrapper) -> bool:
        if self.should_rotate():
            local_formatter = self.parent.formatter()
            
            message.record['message'] = '{text:=^70}'.format(text=" <-- CUT --> ")
            
            for line in local_formatter.format(message.record):
                fileIO.write(line)

            self.rotate_date = self.calc_rotation_date()
            return True
        else:
            return False


class Retentor(IRetentor):

    def __call__(self, filepathes: List[str]) -> NoReturn:
        for filepath in filepathes:
            _, _, fileext = self.split_path(filepath)

            if os.path.getmtime(filepath) < (datetime.now() - timedelta(days=self.parent.log_config.retention_days)).timestamp():
                os.remove(filepath)
                continue
            else:
                if fileext != '.zip':
                    self.parent.compressor()(filepath)


class Compressor(ICompressor):

    def __call__(self, filepath: str) -> NoReturn:
        path, filename, fileext = self.split_path(filepath)
        
        with ZipFile(os.path.join(path, f'{filename}.zip'), mode='w', compression=ZIP_DEFLATED) as zip:
            zip.write(filepath, f'{filename}{fileext}')
            zip.close()

        os.remove(filepath)


class Filter(IFilter):           

    def decide(self, record) -> bool:
        return record['level'].no >= self.parent.levels_case(self.parent.log_config.level)

    def __call__(self, record) -> bool:
        if self.decide(record) == True:
            if self.parent.rotator().should_rotate():
                self.parent.rotated = True
            return True
        else:
            return False
            

class Toolchain(IToolchain):

    def formatter(self) -> IFormatter:
        return Formatter(self)

    def rotator(self) -> IRotator:
        return Rotator(self)

    def retentor(self) -> IRetentor:
        return Retentor(self)

    def compressor(self) -> ICompressor:
        return Compressor(self)

    def filter(self) -> IFilter:
        return Filter(self)
        