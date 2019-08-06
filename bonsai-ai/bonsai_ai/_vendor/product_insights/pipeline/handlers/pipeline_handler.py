from abc import abstractmethod
from collections import deque

from product_insights._type_hints import *
from product_insights.log_manager_resources import LogManagerResources


class PipelineHandler(object):
    input = None  # type: deque[Any]
    output = None  # type: deque[Any]

    def __init__(self, resource_manager, tenant_token, input_=None, output=None):
        # type: (LogManagerResources, str, deque, deque) -> None
        self._resources = resource_manager
        self._tenant_token = tenant_token
        self.input = input_ if input_ is not None else deque()
        self.output = output if output is not None else deque()

    @abstractmethod
    def process_input(self, flush=False):
        # type: (Any, Any) -> None
        raise NotImplementedError('PipelineHandler subclass must implement process_input()')

    @abstractmethod
    def drop(self):
        # type: () -> None
        raise NotImplementedError('PipelineHandler subclasses must implement drop()')
