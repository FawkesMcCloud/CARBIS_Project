from ..abc import IAppConfig
import json


class AppConfigDictAdapter(IAppConfig):
    def __init__(self, data: dict) -> None:
        self.data = data

    def as_str(self) -> str:
        return json.dumps(self.data, indent=2, ensure_ascii=False) 


class AppConfigMetaconfigAdapter(IAppConfig):
    def __init__(self, config_root):
        self.data = config_root

    def as_str(self) -> dict:
        return self.data.__io_class__.serialize(self.data.as_dataset())


class AppConfigFilepathAdapter(IAppConfig):
    def __init__(self, filepath: str, encoding='utf-8') -> None:
        self.filepath = filepath
        self.encoding = encoding
        

    def as_str(self) -> dict:
        try:
            with open(self.filepath, 'r', encoding=self.encoding) as f:
                return f'[{self.filepath}]\n{f.read()}' 
        except FileNotFoundError:
            return f'На момент запуска данные о конфигурации приложения отсутствуют.\nФайл конфигурации будет создан автоматически.'