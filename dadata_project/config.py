import enum
from .parametrica import Field, Fieldset, Metaconfig

class Language(enum.Enum):
    English = "en"
    Russian = "ru"

class General(Fieldset):
    base_url = Field[str]("").label("Base URL")
    api_token = Field[str]("").label("API token")
    language = Field[Language](Language.Russian).label("Language")

class Config(Metaconfig):
    general = Field[General](
        base_url="https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address").label("General API Settings")


