from loguru import logger
from typing import Iterable
import requests

from .sugengine import ISuggestionEngine, Suggestion, Coordinates
from .config import General

class DaDataException(Exception):
    ...

class DaDataAPI(ISuggestionEngine):

    def __init__(self, config: General) -> None:
        self.general_config = config

    def get_suggestions(self, query: str, count: int = 10) -> Iterable[Suggestion]:
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': "Token " + self.general_config.api_token}
        json_data = {'query': query, "language": self.general_config.language.value, "count": count}

        response = requests.post(
            self.general_config.base_url, 
            headers=headers, 
            json=json_data
        )

        logger.success(f"made request:{query}")

        if response.status_code == 200:
            suggestions = [Suggestion(i['value']) for i in response.json()['suggestions']]
            logger.success(f"got response with {response.status_code} recieved {len(suggestions)} ")
            return suggestions
        else:
            raise DaDataException("Что-то пошло не так")

    def get_coordinates(self, suggestion: Suggestion) -> Coordinates:
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': "Token " + self.general_config.api_token}
        json_data = {'query': str(suggestion), "language": self.general_config.language.value, "count": 1}

        response = requests.post(
            self.general_config.base_url, 
            headers=headers, 
            json=json_data
        )

        if response.status_code == 200:
            result = response.json()["suggestions"][0]["data"]
            return Coordinates(result["geo_lat"], result["geo_lon"])
        else:
            raise DaDataException("Что-то пошло не так")
