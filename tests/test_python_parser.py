import pytest

from dataclass_config.parsers import PythonParser


DATA_STR = \
"""
INTEGER = 12

FLOAT = 0.2

STRING = 'STRING'

OBJECT = {123: 'hello', 'hello': 'nope'}

TUPLE = (1, 2, 3)

LIST = [1, 2, 3]

SET = {1, 2, 3}
"""

DATA_OBJ = {
    "INTEGER": 12,
    "FLOAT": 0.2,
    "STRING": "STRING",
    "OBJECT": {
        123: 'hello',
        'hello': 'nope'
    },
    "TUPLE": (1, 2, 3),
    "LIST": [1, 2, 3],
    "SET": {1, 2, 3}
}


def test_parsing():
    parse_result = PythonParser().parse_string(DATA_STR)

    assert parse_result == DATA_OBJ

    with pytest.raises(TypeError):
        parse_result['SET'].discard(1)

    with pytest.raises(TypeError):
        parse_result['LIST'].append(1)

    with pytest.raises(TypeError):
        parse_result['OBJECT'].update({1: 2})


def test_dumping():
    dump_result = PythonParser().update_config('', DATA_OBJ)
    assert ('\n' + dump_result + '\n') == DATA_STR

    assert PythonParser().update_config(
        'abc = 12  # Comment',
        {'hello': 'world'}
    ) == 'abc = 12  # Comment\n\nhello = \'world\''


def test_not_supported_features():
    parser = PythonParser()

    with pytest.raises(ValueError):
        parser.parse_string("(a, b) = 1, 3")

    with pytest.raises(ValueError):
        parser.parse_string("import os")

    with pytest.raises(ValueError):
        parser.parse_string("from os import remove")

    with pytest.raises(ValueError):
        parser.parse_string("a = b")

    with pytest.raises(ValueError):
        parser.parse_string("a = {123: 123, **dict()}")
