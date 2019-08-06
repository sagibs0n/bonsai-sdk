import traceback
import warnings
from functools import wraps


def deprecated(func):
    @wraps(func)
    def run_deprecated(*args, **kwargs):
        stack = traceback.format_stack()[:-1]

        if stack[-1] not in func.__usages:
            func.__usages.add(stack[-1])

            warnings.warn('Deprecated call to ' + func.__name__, stacklevel=2)
            warnings.warn(''.join(stack), stacklevel=2)

        return func(*args, **kwargs)

    func.__usages = set()
    return run_deprecated
