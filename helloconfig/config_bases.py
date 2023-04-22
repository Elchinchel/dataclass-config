from typing import Any, Type
from inspect import isclass
from dataclasses import is_dataclass, dataclass, fields, MISSING

from dataclass_factory import Factory

from helloconfig.exceptions import FieldsMissing
from helloconfig.parsers import (
    AbstractParser,
    PythonParser,
    JsonParser,
    YamlParser,
    EnvParser
)


def get_required_fields(data_cls):
    result = {}
    for field in fields(data_cls):
        if field.default is MISSING and field.default_factory is MISSING:
            result[field.name] = field.type
    return result


def get_all_fields(data_cls):
    return {f.name: f for f in fields(data_cls)}


def try_delattr(obj, name):
    try:
        delattr(obj, name)
    except AttributeError:
        pass


class ConfigBaseMeta(type):
    @staticmethod
    def wrap_nested_classes(klass: type):
        annotations = getattr(klass, '__annotations__', {})
        setattr(klass, '__annotations__', annotations)

        for f_name, f_value in list(klass.__dict__.items()):
            if isclass(f_value):
                if issubclass(f_value, ConfigBase):
                    nested_cls = f_value._dataclass

                    # if following attributes exists
                    # dataclass constructor will raise exception
                    delattr(nested_cls, '__setattr__')
                    delattr(nested_cls, '__delattr__')

                else:
                    nested_cls = f_value

                ConfigBaseMeta.wrap_nested_classes(nested_cls)

                # dataclass() will not overwrite existing init function, so delete it
                # (users should not define any functions in nested config fields,
                #  so assume nobody did and existing __init__ was created by
                #  dataclass constructor with old args (we updated them above))
                try_delattr(nested_cls, '__init__')
                annotations[f_name] = dataclass(frozen=True)(nested_cls)

    def __new__(cls, cls_name, bases, namespace: 'dict[str, Any]'):
        if not bases or bases[0] is ConfigBase:
            return super().__new__(cls, cls_name, bases, namespace)

        klass = super().__new__(cls, cls_name, bases, namespace)

        dc_klass = super().__new__(cls, cls_name, (), namespace)

        ConfigBaseMeta.wrap_nested_classes(dc_klass)

        klass._dataclass = dataclass(frozen=True)(dc_klass)  # type: ignore

        return klass


class ConfigBase(metaclass=ConfigBaseMeta):
    _PARSER_CLS: Type[AbstractParser]

    _dataclass: type
    _data_object: object

    def __getattribute__(self, __name: str):
        try:
            data_obj = object.__getattribute__(self, '_data_object')
            return getattr(data_obj, __name)
        except AttributeError:
            pass

        return object.__getattribute__(self, __name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        raise TypeError('Config object is immutable.')

    def _set_data(self, value):
        return super().__setattr__('_data_object', value)

    @classmethod
    def from_obj(cls, raw_obj: 'dict[str, Any]'):
        obj = Factory().load(raw_obj, cls._dataclass)
        inst = cls()
        inst._set_data(obj)
        return inst

    @classmethod
    def from_str(cls, data: str):
        parser = cls._PARSER_CLS()
        raw_obj = parser.parse_string(data)

        try:
            return cls.from_obj(raw_obj)
        except TypeError:
            rq_fields = get_required_fields(cls._dataclass)
            diff = set(rq_fields).difference(raw_obj.keys())
            if not diff:
                raise
            raise FieldsMissing('Some fields are missing from config '
                               f'({diff!r})') from None

    @classmethod
    def from_file(cls, path: str):
        parser = cls._PARSER_CLS()

        try:
            with open(path, encoding='utf-8') as file:
                raw_config = file.read()
                raw_obj = parser.parse_string(raw_config)
        except FileNotFoundError:
            rq_fields = get_all_fields(cls._dataclass)
            default_config = parser.update_config(
                '', {name: field for name, field in rq_fields.items()}
            )

            with open(path, 'w', encoding='utf-8') as file:
                file.write(default_config)

            raise FieldsMissing('Config file at {path!r} not found. '
                                'New file with empty values created.') from None

        try:
            return cls.from_obj(raw_obj)
        except TypeError:
            rq_fields = get_required_fields(cls._dataclass)
            diff = set(rq_fields).difference(raw_obj.keys())

            if not diff:
                raise

            for field_name in diff:
                raw_obj[field_name] = rq_fields[field_name]()
            updated_config = parser.update_config(raw_config, raw_obj)
            with open(path, 'w', encoding='utf-8') as file:
                file.write(updated_config)

            raise FieldsMissing('Some fields are missing from config. '
                                'File was updated with empty values, '
                               f'check them out. (missing: {diff!r})') from None


class PythonConfig(ConfigBase):
    """
    Uses python syntax for config storage. Parsing performed with AST module,
    only literals supported, no imports, no code evaluation.
    """

    _PARSER_CLS = PythonParser


class JsonConfig(ConfigBase):
    """Json syntax config, comments not supported"""

    _PARSER_CLS = JsonParser


class YamlConfig(ConfigBase):
    """Yaml syntax config, supporting only safe tags"""

    _PARSER_CLS = YamlParser


class DotEnvConfig(ConfigBase):
    """
    Uses .env files syntax.
    Lookup only within specified file, environment variables are ignored.
    """

    _PARSER_CLS = EnvParser
