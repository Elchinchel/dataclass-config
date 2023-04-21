from os import remove
from textwrap import dedent
from tempfile import NamedTemporaryFile, mktemp
from dataclasses import dataclass

import pytest

from dataclass_config.exceptions import FieldsMissing
from dataclass_config.config_bases import PythonConfig


class Config(PythonConfig):
    NUMBER: int
    STRING: str

    DEFAULT_NUMBER = 15
    DEFAULT_STRING = 'hello'


class NestedConfig(PythonConfig):
    value: str

    class some_obj:
        hello: str

        @dataclass
        class some_another_obj:
            hello: str

            class somebody_didnt_read_readme_obj(PythonConfig):
                still_hello: str


NESTED_CFG_FILE = """
value = "yay"

some_obj = {
    "hello": "hi",

    "some_another_obj": {
        "hello": "hi",

        "somebody_didnt_read_readme_obj": {
            "still_hello": "hi"
        }
    }
}
"""


def test_load_from_file():
    with NamedTemporaryFile('r+', delete=False) as file:
        file.write(f'NUMBER = {Config.DEFAULT_NUMBER!r}\n')
        file.write(f'STRING = {Config.DEFAULT_STRING!r}\n')

    try:
        config = Config.from_file(file.name)

        assert config.NUMBER == config.DEFAULT_NUMBER
        assert config.STRING == config.DEFAULT_STRING
    finally:
        remove(file.name)

    with NamedTemporaryFile('r+', delete=False) as file:
        file.write(f'NUMBER = 5\n')
        file.write(f'STRING = 123\n')

    try:
        with pytest.raises(ValueError):
            config = Config.from_file(file.name)
    finally:
        remove(file.name)


def test_add_missing_fields():
    with NamedTemporaryFile('r+', delete=False) as file:
        file.write(f'NUMBER = {Config.DEFAULT_NUMBER!r}\n')
        file.flush()

    try:
        with pytest.raises(FieldsMissing):
            Config.from_file(file.name)

        config = Config.from_file(file.name)

        assert config.NUMBER == config.DEFAULT_NUMBER
        assert config.STRING == str()
    finally:
        remove(file.name)


def test_config_not_exists():
    filename = mktemp()

    with pytest.raises(FieldsMissing):
        Config.from_file(filename)

    try:
        config = Config.from_file(filename)

        assert config.NUMBER == int()
        assert config.STRING == str()
    finally:
        remove(filename)


def test_nested_classes():
    config = NestedConfig.from_str(NESTED_CFG_FILE)

    assert config.some_obj.hello == 'hi'
    assert config.some_obj.some_another_obj.hello == 'hi'
    assert config.some_obj.some_another_obj.somebody_didnt_read_readme_obj.still_hello == 'hi'


def test_attrs():
    @dataclass
    class OneFielder:
        hello: str = 'hi'

    config = Config()
    config._set_data(OneFielder())

    config.hello

    with pytest.raises(AttributeError):
        config.bye

    with pytest.raises(TypeError):
        config.hello = 'bye'  # type: ignore
