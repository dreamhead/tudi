from typing import Any, Callable, List, Optional, Type, TypeVar

from pydantic import BaseModel

from tudi.agent import Agent
from tudi.statements.conditional import When

from .base import Runnable, Task

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)

class Flow(Task):
    def __init__(self, runnable: Task):
        super().__init__()
        self._tasks: List[Runnable] = [runnable]
        self._input_type = runnable.input_type

    def input_type(self) -> Type[InputT]:
        return self._input_type

    @property
    def output_type(self) -> Type[OutputT]:
        if not self._tasks:
            return None

        return self._tasks[-1].output_type

    @classmethod
    def start(cls, task: Task) -> 'Flow':
        return cls(task)

    def next(self, task: Task, map_input: Optional[Callable[[Any], Any]] = None) -> 'Flow':
        self._validate_type_compatibility(task)
        if map_input:
            from tudi.statements import NextStatement
            task = NextStatement(task, map_input)
        self._tasks.append(task)
        return self

    def conditional(self, *conditions: When, default: Optional[Agent] = None) -> 'Flow':
        from tudi.statements import ConditionalStatement
        for condition in conditions:
            if not condition.has_then():
                raise ValueError("Condition must have an agent set using 'then' method")
            condition.validate_type_compatibility(self._tasks[-1])
        if default:
            self._validate_type_compatibility(default)
        statement = ConditionalStatement(list(conditions), default)
        self._tasks.append(statement)
        return self

    def _validate_type_compatibility(self, next_agent: Task) -> None:
        if not self._tasks:
            return

        last_agent = self._tasks[-1]
        if not isinstance(last_agent, Agent):
            return

        from tudi.type_validator import validate_type_compatibility
        validate_type_compatibility(last_agent, next_agent)


    def run(self, input_data: Any) -> Any:
        result = input_data
        for agent in self._tasks:
            result = agent.run(result)
        return result