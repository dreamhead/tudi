from typing import Any, Callable, Optional, Type, TypeVar

from pydantic import BaseModel

from tudi.agent import Agent
from tudi.base import Runnable, Statement

T = TypeVar('T')

class When:
    def __init__(self, predicate: Callable[[Any], bool]):
        self._predicate = predicate
        self._agent: Optional[Agent] = None

    def then(self, agent: Agent) -> 'When':
        self._agent = agent
        return self

    def test(self, input_data: Any) -> bool:
        return self._predicate(input_data)

    def run(self, input_data: Any) -> Any:
        if self._agent:
            return self._agent.run(input_data)
        return None

    @property
    def input_type(self) -> Type[T]:
        return self._agent.input_type if self._agent else None

    @property
    def output_type(self) -> Type[T]:
        return self._agent.output_type if self._agent else None

    def validate_type_compatibility(self, last: Runnable) -> None:
        if not self._agent:
            return

        from tudi.type_validator import validate_type_compatibility
        validate_type_compatibility(last, self._agent)

    def has_then(self) -> bool:
        return self._agent is not None

def when(predicate: Callable[[Any], bool]) -> When:
    return When(predicate)

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)

class ConditionalStatement(Statement):
    def __init__(self, conditions: list[When],
                 default: Optional[Agent] = None,
                 map_input: Optional[Callable[[Any], Any]] = None):
        super().__init__()
        self.conditions = conditions
        self.default = default
        self._input_type = conditions[0].input_type if conditions else None
        self._map_input = map_input or (lambda v: v)

    @property
    def input_type(self) -> Type[InputT]:
        return self._input_type

    @property
    def output_type(self) -> Type[OutputT]:
        if self.default:
            return self.default.output_type
        if self.conditions and self.conditions[-1].output_type:
            return self.conditions[-1].output_type

        return None

    def run(self, input_data: Any) -> Any:
        transformed_input = self._map_input(input_data)
        for condition in self.conditions:
            if condition.test(transformed_input):
                return condition.run(transformed_input)
        if self.default:
            return self.default.run(transformed_input)
        return None