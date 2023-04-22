import pytest

from helloconfig import DotEnvConfig
from helloconfig.parsers import EnvParser


DATA_STR = """
# strings
STRING=STRING
NUMBER=2
"""[1:]

DATA_OBJ = {
    "STRING": "STRING",
    "NUMBER": "2"
}


class Config(DotEnvConfig):
    STRING: str
    NUMBER: int


def test_cast():
    config = Config.from_str(DATA_STR)

    assert isinstance(config.NUMBER, int)


def test_parsing():
    parse_result = EnvParser().parse_string(DATA_STR)

    assert parse_result == DATA_OBJ


def test_dumping():
    dump_result = EnvParser().update_config(DATA_STR, {"TEST": "12"})

    assert dump_result == DATA_STR + '\n\n' + 'TEST=12'