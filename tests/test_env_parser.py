import pytest

from dataclass_config.parsers import EnvParser


DATA_STR = """
# strings
STRING=STRING
"""[1:]

DATA_OBJ = {
    "STRING": "STRING",
}


def test_parsing():
    parse_result = EnvParser().parse_string(DATA_STR)

    assert parse_result == DATA_OBJ


def test_dumping():
    dump_result = EnvParser().update_config(DATA_STR, {"TEST": "12"})

    assert dump_result == DATA_STR + '\n\n' + 'TEST=12'