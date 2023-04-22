def _get_immutable_value(obj):
    if isinstance(obj, dict):
        for key in list(obj.keys()):
            obj[key] = _get_immutable_value(obj[key])
        return ImmutableDict(obj)

    if isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = _get_immutable_value(obj[i])
        return ImmutableList(obj)

    if isinstance(obj, set):
        return ImmutableSet(_get_immutable_value(val) for val in obj)

    return obj


def replace_mutable_values(obj: dict):
    return _get_immutable_value(obj)


def _not_supported_method(method_name: str):
    def placeholder(self: object, *args, **kwargs):
        cls_name = self.__class__.__name__
        raise TypeError(f'Config value {cls_name} does not '
                        f'suppport \'{method_name}\' method')
    return placeholder


class ImmutableDict(dict):
    pop = _not_supported_method('pop')
    clear = _not_supported_method('clear')
    update = _not_supported_method('update')
    popitem = _not_supported_method('popitem')
    setdefault = _not_supported_method('setdefault')

    __setitem__ = _not_supported_method('__setitem__')
    __delitem__ = _not_supported_method('__delitem__')


class ImmutableList(list):
    pop = _not_supported_method('pop')
    sort = _not_supported_method('sort')
    clear = _not_supported_method('clear')
    append = _not_supported_method('append')
    extend = _not_supported_method('extend')
    insert = _not_supported_method('insert')
    insert = _not_supported_method('insert')
    remove = _not_supported_method('remove')
    reverse = _not_supported_method('reverse')

    __setitem__ = _not_supported_method('__setitem__')
    __delitem__ = _not_supported_method('__delitem__')


# this is more verbose, than just use frozenset
class ImmutableSet(set):
    add = _not_supported_method('add')
    pop = _not_supported_method('pop')
    clear = _not_supported_method('clear')
    remove = _not_supported_method('remove')
    update = _not_supported_method('update')
    discard = _not_supported_method('discard')
    difference_update = _not_supported_method('difference_update')
    intersection_update = _not_supported_method('intersection_update')
    symmetric_difference_update = _not_supported_method('symmetric_difference_update')
