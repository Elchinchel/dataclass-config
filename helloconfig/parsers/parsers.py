import ast
import json
import configparser

from io import StringIO
from abc import ABC, abstractmethod
from typing import Any
from dataclasses import (
    MISSING, is_dataclass,
    Field as DataclassField,
    fields as dataclass_fields,
)

import yaml

from helloconfig.parsers.base import AbstractParser
from helloconfig.immutable import (
    ImmutableDict, ImmutableList, ImmutableSet,
    replace_mutable_values
)


class JsonParser(AbstractParser):
    def _object_pairs_hook(self, pairs):
        result = {}
        for name, value in pairs:
            if isinstance(value, list):
                value = ImmutableList(value)
            result[name] = value
        return ImmutableDict(result)

    def parse_string(self, data: str) -> 'dict[str, Any]':
        return json.loads(data, object_pairs_hook=self._object_pairs_hook)

    def update_config(self, config: str, fields: 'dict[str, Any]') -> str:
        if config:
            obj = json.loads(config)
            obj.update(fields)
        else:
            obj = fields
        return json.dumps(obj, ensure_ascii=False, indent=4)


class YamlParser(AbstractParser):
    def parse_string(self, data: str) -> 'dict[str, Any]':
        obj = yaml.safe_load(data)
        return replace_mutable_values(obj)  # type: ignore

    def update_config(self, config: str, fields: 'dict[str, Any]') -> str:
        fields_str = yaml.safe_dump(fields, indent=4)
        if config:
            return config + '\n\n' + fields_str
        return fields_str


class IniParser(AbstractParser):
    def parse_string(self, data: str) -> 'dict[str, Any]':
        parser = configparser.ConfigParser()
        parser.read_string(data)
        values = dict(parser[parser.default_section].items())
        for section in parser.sections():
            values.update(dict(parser[section].items()))
        return replace_mutable_values(values)  # type: ignore

    def update_config(self, config: str, fields: 'dict[str, Any]') -> str:
        parser = configparser.ConfigParser()
        parser.update(fields)
        fields_str = StringIO()
        parser.write(fields_str)
        if config:
            return config + '\n\n' + fields_str.getvalue()
        return fields_str.getvalue()


class EnvParser(AbstractParser):
    def parse_string(self, data: str) -> 'dict[str, Any]':
        result = {}
        for line in data.splitlines():
            name, sep, value = line.partition('=')
            if not sep:
                continue

            result[name.strip()] = value.strip()

        return result

    def update_config(self, config: str, fields: 'dict[str, Any]') -> str:
        lines = []
        for name, value in fields.items():
            lines.append(f'{name}={value}')
        fields_str = '\n\n'.join(lines)
        if config:
            return config + '\n\n' + fields_str
        return fields_str  # pragma: no cover
