from typing import Any
from dataclasses import (
    MISSING, is_dataclass,
    Field as DataclassField,
    fields as dataclass_fields,
)

import libcst

from helloconfig.parsers.base import AbstractParser
from helloconfig.immutable import (
    ImmutableDict, ImmutableList, ImmutableSet
)


class NameSpace(dict):
    "Represents nested namespace"


_literal_expr_types = (
    libcst.Integer,
    libcst.Float,
    libcst.SimpleString
)

_literal_types = {
    int: libcst.Integer,
    str: libcst.SimpleString,
    float: libcst.Float,
}

_seq_types = {
    set: libcst.Set,
    list: libcst.List,
    tuple: libcst.Tuple,
}


def _get_dict_elt(expr: 'libcst.StarredDictElement | libcst.DictElement'):
    if isinstance(expr, libcst.StarredDictElement):
        raise ValueError('Starred elements are not supported')
    if not isinstance(expr.key, _literal_expr_types):
        raise ValueError('Dictionary key must be a literal')
    return (_get_expr_value(expr.key), _get_expr_value(expr.value))


def _get_seq_elt(expr: libcst.BaseElement):
    if isinstance(expr, libcst.StarredElement):
        raise ValueError('Starred elements are not supported')
    return _get_expr_value(expr.value)


def _get_expr_value(expr: libcst.BaseExpression):
    if isinstance(expr, _literal_expr_types):
        return expr.evaluated_value

    if isinstance(expr, libcst.List):
        return ImmutableList([
            _get_seq_elt(item) for item in expr.elements
        ])

    if isinstance(expr, libcst.Set):
        return ImmutableSet({
            _get_seq_elt(item) for item in expr.elements
        })

    if isinstance(expr, libcst.Dict):
        return ImmutableDict({
            _get_dict_elt(item) for item in expr.elements  # type: ignore
        })

    if isinstance(expr, libcst.Tuple):
        return tuple(_get_seq_elt(item) for item in expr.elements)

    if isinstance(expr, libcst.Name):
        raise ValueError('Referencing variables is not supported '
                         'in config files')

    raise ValueError(f'Unsupported expression type ({expr!r})')  # pragma: no cover


def _make_assign(target: str, value: libcst.BaseExpression):
    return libcst.Assign(
        [libcst.AssignTarget(libcst.Name(target))],
        value
    )


def _make_expr(value: Any):
    try:
        return libcst.parse_expression(repr(value))
    except Exception as e:
        raise


def _make_seq_elt(value: Any):
    expr = _make_expr(value)
    return libcst.Element(expr)


def _make_dict_elt(name: str, value: Any):
    expr = _make_expr(value)
    return libcst.DictElement(libcst.Name(name), expr)


class LoadVisitor:
    def __init__(self) -> None:
        self.fields = {}
        self.stack = [self.fields]

    @property
    def current_ns(self) -> 'dict[str, Any]':
        return self.stack[-1]

    def visit_Assign(self, node: libcst.Assign) -> 'bool | None':
        for assign_target in node.targets:
            target = assign_target.target
            if not isinstance(target, libcst.Name):
                raise ValueError('Multiple assign is '
                                 'not supported in config files')
            self.current_ns[target.value] = _get_expr_value(node.value)

    def visit_Import(self, node):
        raise ValueError('Imports are not supported in config files')

    def visit_ImportFrom(self, node) -> Any:
        raise ValueError('Imports are not supported in config files')


class FieldLoader(LoadVisitor, libcst.CSTVisitor):
    def visit_ClassDef(self, node: libcst.ClassDef) -> 'bool | None':
        namespace = {}
        self.current_ns[node.name.value] = namespace
        self.stack.append(namespace)

    def leave_ClassDef(self, node: libcst.ClassDef):
        self.stack.pop()


class FieldUpdater(LoadVisitor, libcst.CSTTransformer):
    def __init__(self, required_fields: 'dict[str, Any]') -> None:
        super().__init__()
        self.path = []
        self.required_fields = required_fields

    @property
    def current_ns_required(self) -> 'dict[str, Any] | None':
        path = self.path.copy()
        required_ns = self.required_fields
        while path and (required_ns is not None):
            required_ns = required_ns.get(path.pop())
        return required_ns

    def leave_Module(self, original_node: libcst.Module, updated_node: libcst.Module):
        required_ns = self.current_ns_required
        current_ns = self.current_ns

        if required_ns is None:
            return updated_node

        missing_fields = set(required_ns.keys()).difference(current_ns.keys())
        if not missing_fields:
            return updated_node

        print(updated_node)

        new_nodes = self._construct_missing_nodes(
            {n: required_ns[n] for n in missing_fields}
        )
        new_nodes.extend(original_node.body)
        return updated_node.with_changes(body=new_nodes)

    def _construct_node(self, name: str, value):
        val_type = type(value)

        if val_type in _literal_types:
            return _make_assign(name, _make_expr(value))

        if val_type in _seq_types:
            literal = _seq_types[val_type]([_make_seq_elt(v) for v in value])
            return _make_assign(name, literal)

        if val_type == dict:
            literal = libcst.Dict(
                [_make_dict_elt(k, v) for k, v in value.items()]
            )
            return _make_assign(name, literal)

        if isinstance(value, DataclassField):
            if value.default_factory is not MISSING:
                default = value.default_factory()
            elif value.default is not MISSING:
                default = value.default
            else:
                default = value.type()
            return self._construct_node(name, default)

        if is_dataclass(value):
            cls_def = libcst.ClassDef(
                libcst.Name(name),
                libcst.SimpleStatementSuite([])
            )
            self.visit_ClassDef(cls_def)
            return self.leave_ClassDef(cls_def, cls_def)

        raise ValueError(f'Unsupported type {val_type!r}')

    def _construct_missing_nodes(
            self,
            missing_ns: 'dict[str, Any]'
    ) -> 'list[libcst.SimpleStatementLine | libcst.BaseCompoundStatement]':
        nodes = []

        for name, value in missing_ns.items():
            nodes.append(self._construct_node(name, value))

        return nodes

    def visit_ClassDef(self, node: libcst.ClassDef) -> 'bool | None':
        namespace = {}
        self.current_ns[node.name.value] = namespace
        self.path.append(node.name.value)
        self.stack.append(namespace)

    def leave_ClassDef(self, original_node: libcst.ClassDef, updated_node: libcst.ClassDef):
        required_ns = self.current_ns_required
        current_ns = self.current_ns

        self.path.pop()
        self.stack.pop()

        if required_ns is None:
            return updated_node

        missing_fields = set(required_ns.keys()).difference(current_ns.keys())
        if not missing_fields:
            return updated_node

        print(updated_node)

        return updated_node


class PythonParser(AbstractParser):
    def parse_string(self, data: str) -> 'dict[str, Any]':
        visitor = FieldLoader()
        libcst.parse_module(data).visit(visitor)
        return visitor.fields

    def update_config(self, config: str, fields: 'dict[str, Any]') -> str:
        visitor = FieldUpdater(fields)
        module = libcst.parse_module(config)
        return module.visit(visitor).code

    def _dump_field(self, name, value, stack: list) -> str:
        if len(stack) > 16:  #  pragma: no cover
            raise ValueError('Something definitely '
                             'wrong with your config structure. It\'s too deep.')

        if hasattr(value, '_dataclass') and is_dataclass(value._dataclass):
            value = value._dataclass

        if is_dataclass(value):
            dumped = [f'class {name}:']
            for field in dataclass_fields(value):
                dumped.append(
                    self._dump_field(field.name, field, stack + [type]))
            dumped_val = (len(stack) *  '    ') + '\n'.join(dumped)
            if stack and stack[-1] is type:
                dumped_val = '\n' + dumped_val
            return dumped_val

        if isinstance(value, DataclassField):
            if value.default_factory is not MISSING:
                default = value.default_factory()
            elif value.default is not MISSING:
                default = value.default
            else:
                default = value.type()
            return self._dump_field(name, default, stack)

        if isinstance(value, dict):
            dumped = [f'{name} = {{']
            for k,v in value.items():
                val = self._dump_field(k, v, stack + [dict])
                dumped.append(val + ',')
            indent = (len(stack) *  '    ')
            return indent + '\n'.join(dumped) + '\n' + indent + '}'

        if stack and stack[0] is dict:
            return (len(stack) *  '    ') + f'{name!r}: {value!r}'

        return (len(stack) *  '    ') + f'{name} = {value!r}'
