from helloconfig import DotEnvConfig
from dataclass_factory import validate


class Config(DotEnvConfig):
    host: str
