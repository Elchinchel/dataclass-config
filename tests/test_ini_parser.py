import pytest

from helloconfig.parsers import IniParser


DATA_STR = """
INTEGER = 12
STRING = "STRING"
"""

DATA_OBJ = {
    "INTEGER": 12,
    "STRING": "STRING",
    # "FLOAT": 0.2,
    # "OBJECT": {
    #     'hello': 'nope'
    # },
    # "LIST": [1, 2, 3],
}


def test_parsing():
    parse_result = IniParser().parse_string(DATA_STR)

    assert parse_result == DATA_OBJ


def test_dumping():
    dump_result = IniParser().update_config('', DATA_OBJ)

    assert dump_result == DATA_STR
