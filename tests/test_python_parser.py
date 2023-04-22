import pytest

from os import remove
from tempfile import mktemp
from dataclasses import dataclass, field

from helloconfig import PythonConfig, FieldsMissing
from helloconfig.parsers import PythonParser


DATA_STR = \
"""
INTEGER = 12

FLOAT = 0.2

STRING = 'STRING'

OBJECT = {
    123: 'hello',
    'hello': 'nope',
}

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


class NestedConfig(PythonConfig):
    value: str

    class some_obj:
        hello: str

        @dataclass
        class some_another_obj:
            hello: str

            are_you_okay: dict = field(default_factory=lambda: ({
                'hello': 'WHY SO MANY GREETINGS THERE',
                123: 321
            }))

            class somebody_didnt_read_readme_obj(PythonConfig):
                still_hello: str


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


def test_nested_dumping():
    filename = mktemp()

    with pytest.raises(FieldsMissing):
        NestedConfig.from_file(filename)

    with open(filename, encoding='utf-8') as file:
        data_written = file.read()
        print(data_written)

    try:
        config = NestedConfig.from_file(filename)
    finally:
        remove(filename)


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
