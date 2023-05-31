import pytest

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


NESTED_DATA_STR = '''
value = 'a'

class some_obj:
    hello = 'b'

    @dataclass
    class some_another_obj:
        hello = 'c'

        are_you_okay = {
            'hello': 'WHY SO MANY GREETINGS THERE',
            123: 321
        }

        class somebody_didnt_read_readme_obj(PythonConfig):
            still_hello = 'd'
'''


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


def test_nested_dumping(tmp_filename):
    with pytest.raises(FieldsMissing):
        NestedConfig.from_file(tmp_filename)

    with open(tmp_filename, encoding='utf-8') as file:
        data_written = file.read()
        print(data_written)

    config = NestedConfig.from_file(tmp_filename)


def test_nested_loading():
    config = NestedConfig.from_str(NESTED_DATA_STR)

    assert config.value == 'a'
    assert config.some_obj.hello == 'b'
    assert config.some_obj.some_another_obj.hello == 'c'
    assert config.some_obj.some_another_obj.somebody_didnt_read_readme_obj.still_hello == 'd'


def test_field_update(tmp_filename):
    class InitialConfig(PythonConfig):
        a: str

        class nested:
            b: str


    class UpdatedConfig(PythonConfig):
        a: str
        a1: int

        class nested:
            b: str
            b1: int

            @dataclass
            class more_nested:
                c: dict = field(default_factory=lambda: {'hi': 'hello'})


    with pytest.raises(FieldsMissing):
        InitialConfig.from_file(tmp_filename)

    config = InitialConfig.from_file(tmp_filename)
    assert config.a == str()
    assert config.nested.b == str()

    with pytest.raises(FieldsMissing):
        UpdatedConfig.from_file(tmp_filename)

    config = UpdatedConfig.from_file(tmp_filename)
    assert config.a1 == int()
    assert config.nested.b1 == int()
    assert config.nested.more_nested == {'hi': 'hello'}


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
