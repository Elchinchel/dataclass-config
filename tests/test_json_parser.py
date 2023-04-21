import pytest

from dataclass_config.parsers import JsonParser


DATA_STR = """{
    "INTEGER": 12,
    "FLOAT": 0.2,
    "STRING": "STRING",
    "OBJECT": {
        "hello": "nope"
    },
    "LIST": [
        1,
        2,
        3
    ]
}"""

DATA_OBJ = {
    "INTEGER": 12,
    "FLOAT": 0.2,
    "STRING": "STRING",
    "OBJECT": {
        'hello': 'nope'
    },
    "LIST": [1, 2, 3],
}


def test_parsing():
    parse_result = JsonParser().parse_string(DATA_STR)

    assert parse_result == DATA_OBJ

    with pytest.raises(TypeError):
        parse_result['LIST'].append(1)

    with pytest.raises(TypeError):
        parse_result['OBJECT'].update({1: 2})


def test_dumping():
    dump_result = JsonParser().update_config('', DATA_OBJ)

    assert dump_result == DATA_STR

    assert JsonParser().update_config(
        '{ "abc": 12 }',
        {'hello': 'world'}
    ) == '{\n    "abc": 12,\n    "hello": "world"\n}'