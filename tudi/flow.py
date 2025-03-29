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

    def map(self, mapper: Callable[[Any], Any]) -> 'Flow':
        from tudi.statements import MapStatement
        task = MapStatement(mapper, self._tasks[-1].output_type)
        self._tasks.append(task)

        self._on_new_runnable(task)
        return self

    def next(self, task: Task) -> 'Flow':
        self._validate_type_compatibility(task)
        from tudi.statements import NextStatement
        task = NextStatement(task)
        self._tasks.append(task)
        # 添加钩子函数，设置前一个MapStatement的output_type
        self._on_new_runnable(task)
        return self

    def _create_conditional_statement(self, conditions: list[When], default: Optional[Agent] = None) -> 'ConditionalStatement':
        from tudi.statements import ConditionalStatement
        for condition in conditions:
            if not condition.has_then():
                raise ValueError("Condition must have an agent set using 'then' method")
            condition.validate_type_compatibility(self._tasks[-1])
        if default:
            self._validate_type_compatibility(default)
        return ConditionalStatement(conditions, default)

    def conditional(self, *conditions: When,
                    default: Optional[Agent] = None) -> 'Flow':
        statement = self._create_conditional_statement(list(conditions), default)
        self._tasks.append(statement)
        # 添加钩子函数，设置前一个MapStatement的output_type
        self._on_new_runnable(statement)
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

    def _on_new_runnable(self, runnable: Runnable) -> None:
        self._set_previous_map_output_type()

    def _set_previous_map_output_type(self) -> None:
        """设置前一个MapStatement的output_type为当前任务的input_type"""
        if len(self._tasks) < 2:
            return

        prev_task = self._tasks[-2]
        current_task = self._tasks[-1]

        from tudi.statements import MapStatement
        if isinstance(prev_task, MapStatement) and prev_task.output_type is None:
            prev_task.output_type = current_task.input_type