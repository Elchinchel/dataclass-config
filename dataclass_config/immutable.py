def not_supported_method(method_name: str):
    def placeholder(self: object, *args, **kwargs):
        cls_name = self.__class__.__name__
        raise TypeError(f'{cls_name} does not '
                        f'suppport \'{method_name}\' method')
    return placeholder


class ImmutableDict(dict):
    pop = not_supported_method('pop')
    clear = not_supported_method('clear')
    update = not_supported_method('update')
    popitem = not_supported_method('popitem')
    setdefault = not_supported_method('setdefault')

    __setitem__ = not_supported_method('__setitem__')
    __delitem__ = not_supported_method('__delitem__')


class ImmutableList(list):
    pop = not_supported_method('pop')
    sort = not_supported_method('sort')
    clear = not_supported_method('clear')
    append = not_supported_method('append')
    extend = not_supported_method('extend')
    insert = not_supported_method('insert')
    insert = not_supported_method('insert')
    remove = not_supported_method('remove')
    reverse = not_supported_method('reverse')

    __setitem__ = not_supported_method('__setitem__')
    __delitem__ = not_supported_method('__delitem__')


class ImmutableSet(set):
    add = not_supported_method('add')
    pop = not_supported_method('pop')
    clear = not_supported_method('clear')
    remove = not_supported_method('remove')
    update = not_supported_method('update')
    discard = not_supported_method('discard')
    difference_update = not_supported_method('difference_update')
    intersection_update = not_supported_method('intersection_update')
    symmetric_difference_update = not_supported_method('symmetric_difference_update')
