from helloconfig import PythonConfig


class Config(PythonConfig):
    user: str
    port: int


config = Config.from_file('config.pyi')
