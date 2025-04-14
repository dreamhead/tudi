from typing import Any, Callable, Optional, Type, TypeVar

from pydantic import BaseModel

from tudi.agent import Agent
from tudi.base import Runnable, Statement

T = TypeVar('T')

class When:
    def __init__(self, predicate: Callable[[Any], bool], default: bool = False):
        self._predicate = predicate
        self._agent: Optional[Agent] = None
        self._output_mapper: Optional[Callable[[Any], Any]] = None
        self._default = default

    def then(self, agent: Agent) -> 'When':
        self._agent = agent
        return self
        
    def to_output(self, mapper: Callable[[Any], Any]) -> 'When':
        self._output_mapper = mapper
        return self

    def test(self, input_data: Any) -> bool:
        return self._predicate(input_data)

    def run(self, input_data: Any) -> Any:
        if not self._agent:
            return None
            
        result = self._agent.run(input_data)
        if self._output_mapper:
            return self._output_mapper(result)
        return result

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

    def has_output_mapper(self) -> bool:
        return self._output_mapper is not None

    def is_default(self) -> bool:
        return self._default

def when(predicate: Callable[[Any], bool]) -> When:
    return When(predicate)

def default(agent: Agent) -> When:
    return When(lambda _: True, True).then(agent)

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)

class CaseStatement(Statement):
    def __init__(self, conditions: list[When],
                 output_type: Optional[Type[OutputT]] = None):
        super().__init__()
        _default, non_default = self._split_conditions(conditions)
        self.conditions = non_default
        self.default = _default
        self._input_type = conditions[0].input_type if conditions else None
        self._output_type = self._as_output_type(output_type)

    @property
    def input_type(self) -> Type[InputT]:
        return self._input_type

    @property
    def output_type(self) -> Type[OutputT]:
        if self._output_type:
            return self._output_type

    def run(self, input_data: Any) -> Any:
        result = None
        
        for condition in self.conditions:
            if condition.test(input_data):
                result = condition.run(input_data)
                break
        else:
            if self.default:
                result = self.default.run(input_data)
                
        if result is not None and self._output_type:
            if not isinstance(result, self._output_type):
                raise TypeError(f"Expected return type {self._output_type.__name__}, got {type(result).__name__}")
                
        return result

    def _as_output_type(self, output_type):
        if output_type:
            return output_type
        if self.conditions and self.conditions[-1].output_type:
            return self.conditions[-1].output_type

    def _split_conditions(self, conditions:list[When]) -> tuple[Optional[When], list[When]]:
        default_conditions = [cond for cond in conditions if cond.is_default()]
        non_default_conditions = [cond for cond in conditions if not cond.is_default()]

        if len(default_conditions) > 1:
            raise ValueError("Multiple default conditions found!")

        return default_conditions[0] if default_conditions else None, non_default_conditions