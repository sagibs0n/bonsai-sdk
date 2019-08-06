from product_insights._type_hints import *
from product_insights.pii_kind import PiiKind


# TODO: Is this class thread-safe? Might not be
class Context(object):
    _children = None  # type: Set[Context]

    def __init__(self):
        # type: () -> None
        self._context = {}
        self._cached = {}
        self._parent = {}

        self._children = set()

    def create_child_context(self):
        # type: () -> Context
        child = Context()
        child._update_cache(self._cached)

        self._children.add(child)

        return child

    def set_context(self, key, value, pii_kind=PiiKind.PiiKind_None):
        # type: (str, Any, int) -> None
        self._context[key] = (value, pii_kind)
        self._cached[key] = (value, pii_kind)

        for child in self._children:
            child._update_cache(self._cached)

    def clear_context(self):
        # type: () -> None
        self._context = {}
        self._cached = self._parent.copy()

        for child in self._children:
            child._update_cache(self._cached)

    def get_context(self):
        # type: () -> Dict[str, Tuple[Any, int]]
        return self._cached

    def _update_cache(self, parent_context):
        # type: (Dict[str, Tuple[Any, int]]) -> None

        self._parent = parent_context
        self._cached = parent_context.copy()
        self._cached.update(self._context)

        for child in self._children:
            child._update_cache(self._cached)
