from typing import Any, Callable, Optional, TypeVar

from tudi.agent import Agent
from tudi.base import BaseRunnable

T = TypeVar('T')

class When:
    def __init__(self, condition: Callable[[Any], bool]):
        self.condition = condition
        self.agent: Optional[Agent] = None

    def then(self, agent: Agent) -> 'When':
        self.agent = agent
        return self

def when(condition: Callable[[Any], bool]) -> When:
    return When(condition)

class ConditionalRunnable(BaseRunnable):
    def __init__(self, conditions: list[When], default: Optional[Agent] = None):
        self.conditions = conditions
        self.default = default

    def run(self, input_data: Any) -> Any:
        for condition in self.conditions:
            if condition.condition(input_data):
                return condition.agent.run(input_data)
        if self.default:
            return self.default.run(input_data)
        return input_data