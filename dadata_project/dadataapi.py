from ast import Import
from dadata_project.parametrica.io import YAMLFileConfigIO
from sugengine import ISuggestionEngine, Suggestion, Coordinates
from typing import Iterable
from config import Config

import requests

class DaDataAPI(ISuggestionEngine):

    def __init__(self, config:Config) -> None:
        self.config = config

    def do_suggest(self, query: str) -> Iterable[Suggestion]:

        url = self.config.general.base_url
        token = "Token" + self.config.general.api_token
        language = self.config.general.language

        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': token}
        json_data = {'query': query, "language": language}

        response = requests.post(url, headers=headers, json = json_data)

        suggestions = []
        for i in response.json["suggestions"]:
            suggestions.append(i["value"])
        
        return suggestions

    def do_get_coords(self, addres: Suggestion) -> Coordinates:
        return super().do_get_coords()

