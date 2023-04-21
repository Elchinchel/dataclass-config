import ast
import json
import configparser

from io import StringIO
from abc import ABC, abstractmethod
from typing import Any

import yaml

from dataclass_config.immutable import (
    ImmutableDict, ImmutableList, ImmutableSet
)


class AbstractParser(ABC):  # pragma: no cover
    @abstractmethod
    def parse_string(self, data: str) -> 'dict[str, Any]':
        raise NotImplementedError

    @abstractmethod
    def update_config(self, config: str, fields: 'dict[str, Any]') -> str:
        raise NotImplementedError


class PythonParser(AbstractParser):
    class NodeVisitor(ast.NodeVisitor):
        fields_found: 'dict[str, Any]'

        def __init__(self) -> None:
            self.fields_found = {}

        @classmethod
        def _get_value(cls, expr: ast.expr):
            if isinstance(expr, ast.Constant):
                return expr.value

            if isinstance(expr, ast.List):
                value = [cls._get_value(item) for item in expr.elts]
                return ImmutableList(value)

            if isinstance(expr, ast.Set):
                value = {cls._get_value(item) for item in expr.elts}
                return ImmutableSet(value)

            if isinstance(expr, ast.Dict):
                items = zip(expr.keys, expr.values)

                def check_key(key: 'ast.expr | None'):
                    if key is None:
                        raise ValueError('Dictionary unpacking is '
                                         'not supported in config file'
                                        f'(line {expr.lineno})')
                    return key

                value = {cls._get_value(check_key(k)): cls._get_value(v) for k, v in items}
                return ImmutableDict(value)

            if isinstance(expr, ast.Tuple):
                return tuple(cls._get_value(item) for item in expr.elts)

            if isinstance(expr, ast.Name):
                raise ValueError('Referencing variables is not supported '
                                f'in config files (line {expr.lineno})')

            raise ValueError(f'Unsupported expression type ({expr!r}), '
                             f'line {expr.lineno}')  # pragma: no cover

        def visit_Assign(self, node: ast.Assign) -> Any:
            for target in node.targets:
                if not isinstance(target, ast.Name):
                    raise ValueError('Multiple assign is not supported '
                                    f'in config files ({target.lineno})')
                self.fields_found[target.id] = self._get_value(node.value)

        def visit_Import(self, node):
            raise ValueError('Imports are not supported in config files')

        def visit_ImportFrom(self, node) -> Any:
            raise ValueError('Imports are not supported in config files')

    def parse_string(self, data: str) -> 'dict[str, Any]':
        visitor = self.NodeVisitor()
        visitor.visit(ast.parse(data))
        return visitor.fields_found

    def update_config(self, config: str, fields: 'dict[str, Any]') -> str:
        lines = []
        for name, value in fields.items():
            lines.append(f'{name} = {value!r}')
        fields_str = '\n\n'.join(lines)
        if config:
            return config + '\n\n' + fields_str
        return fields_str


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
        return yaml.safe_load(data)

    def update_config(self, config: str, fields: 'dict[str, Any]') -> str:
        fields_str = yaml.safe_dump(fields, indent=4)
        if config:
            return config + '\n\n' + fields_str
        return fields_str


class IniParser(AbstractParser):
    def parse_string(self, data: str) -> 'dict[str, Any]':
        parser = configparser.ConfigParser()
        parser.read(data)
        return {k: v for k, v in parser.items()}

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
