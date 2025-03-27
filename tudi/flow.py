from typing import Any, List, Optional, Type, TypeVar

from pydantic import BaseModel

from tudi.agent import Agent
from tudi.conditional import When

from .base import BaseRunnable

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)

class Flow(BaseRunnable):
    def __init__(self, runnable: BaseRunnable):
        super().__init__()
        self._runnables: List[BaseRunnable] = [runnable]
        self._input_type = runnable.input_type

    def input_type(self) -> Type[InputT]:
        return self._input_type

    @property
    def output_type(self) -> Type[OutputT]:
        if not self._runnables:
            return None
        return self._runnables[-1].output_type

    @classmethod
    def start(cls, agent: Agent) -> 'Flow':
        return cls(agent)

    def next(self, agent: Agent) -> 'Flow':
        self._validate_type_compatibility(agent)
        self._runnables.append(agent)
        return self

    def conditional(self, *conditions: When, default: Optional[Agent] = None) -> 'Flow':
        from tudi.conditional import ConditionalRunnable
        for condition in conditions:
            if not condition.has_then():
                raise ValueError("Condition must have an agent set using 'then' method")
            condition.validate_type_compatibility(self._runnables[-1])
        if default:
            self._validate_type_compatibility(default)
        conditional_agent = ConditionalRunnable(list(conditions), default)
        self._runnables.append(conditional_agent)
        return self

    def _validate_type_compatibility(self, next_agent: Agent) -> None:
        if not self._runnables:
            return

        last_agent = self._runnables[-1]
        if not isinstance(last_agent, Agent):
            return

        from tudi.type_validator import validate_type_compatibility
        validate_type_compatibility(last_agent, next_agent)


    def run(self, input_data: Any) -> Any:
        result = input_data
        for agent in self._runnables:
            result = agent.run(result)
        return result