from typing import Iterable

from dataclasses import dataclass

@dataclass
class Suggestion():
    addr: str

    def __str__(self) -> str:
        return self.addr


@dataclass
class Coordinates():
    lat: float
    lon: float

    def __str__(self) -> str:
        return f"Широта:{self.lat} Долгота:{self.lon}" if self.lat and self.lon is not None else "Нет точных координат"


class ISuggestionEngine():
    # Get suggestions with given query
    def get_suggestions(query:str) -> Iterable[Suggestion]:
        pass
    
    # Get coordinates of given suggestion
    def get_coordinates(addr:Suggestion) -> Coordinates:
        pass