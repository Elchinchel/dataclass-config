import pytest

from helloconfig.parsers import YamlParser


DATA_STR_LIST = """LIST:\n- 1\n- 2\n- 3\n"""
DATA_STR_FLOAT = """FLOAT: 0.2\n"""
DATA_STR_STRING = """STRING: STRING\n"""
DATA_STR_OBJECT = """OBJECT:\n    123: hello\n    hello: nope\n"""
DATA_STR_INTEGER = """INTEGER: 12\n"""

DATA_OBJ = {
    "INTEGER": 12,
    "FLOAT": 0.2,
    "STRING": "STRING",
    "OBJECT": {
        123: 'hello',
        'hello': 'nope'
    },
    "LIST": [1, 2, 3],
}


def test_parsing():
    parse_result = YamlParser().parse_string('\n'.join([
        DATA_STR_LIST,
        DATA_STR_FLOAT,
        DATA_STR_STRING,
        DATA_STR_OBJECT,
        DATA_STR_INTEGER,
    ]))

    assert parse_result == DATA_OBJ

    with pytest.raises(TypeError):
        parse_result['LIST'].append(1)

    with pytest.raises(TypeError):
        parse_result['OBJECT'].update({1: 2})


def test_dumping():
    parser = YamlParser()

    assert parser.update_config('', {"LIST": DATA_OBJ["LIST"]}) == DATA_STR_LIST
    assert parser.update_config('', {"FLOAT": DATA_OBJ["FLOAT"]}) == DATA_STR_FLOAT
    assert parser.update_config('', {"STRING": DATA_OBJ["STRING"]}) == DATA_STR_STRING
    assert parser.update_config('', {"OBJECT": DATA_OBJ["OBJECT"]}) == DATA_STR_OBJECT
    assert parser.update_config('', {"INTEGER": DATA_OBJ["INTEGER"]}) == DATA_STR_INTEGER

    assert parser.update_config(
        'abc: 12 # Comment',
        {'hello': 'world'}
    ) == 'abc: 12 # Comment\n\nhello: world\n'
