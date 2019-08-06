import warnings

from product_insights._type_hints import *


def proxify_method(obj, method, name, pre_exec=None, post_exec=None, deprecation_warning=None):
    # type: (object, Callable[..., Any], str, Callable[..., Any], Callable[..., Any], bool) -> None
    method = _get_full_func(method, pre_exec, post_exec)
    method = _get_deprecated_func(method, name, deprecation_warning)

    obj.__dict__[name] = method


def _get_deprecated_func(method, name, deprecation_warning):
    if deprecation_warning is None:
        return method

    if type(deprecation_warning) is bool:
        message = '{name} is deprecated; use {newname} instead'.format(name=name, newname=method.__name__)
    else:
        message = deprecation_warning

    def method_(*args, **kwargs):
        warnings.warn(message, Warning, stacklevel=2)
        method(*args, **kwargs)

    return method_


def _get_full_func(method, pre_exec, post_exec):
    if pre_exec is not None and post_exec is not None:
        def method_(*args, **kwargs):
            pre_exec(*args, **kwargs)
            method(*args, **kwargs)
            post_exec(*args, **kwargs)
    elif pre_exec is not None:
        def method_(*args, **kwargs):
            pre_exec(*args, **kwargs)
            method(*args, **kwargs)
    elif post_exec is not None:
        def method_(*args, **kwargs):
            method(*args, **kwargs)
            post_exec(*args, **kwargs)
    else:
        method_ = method

    return method_
