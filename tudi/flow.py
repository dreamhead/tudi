from typing import Any, List, Optional

from tudi.agent import Agent
from tudi.conditional import When
from .base import BaseRunnable


class Flow(BaseRunnable):
    def __init__(self, agent: Agent):
        self.agents: List[BaseRunnable] = [agent]

    @classmethod
    def start(cls, agent: Agent) -> 'Flow':
        return cls(agent)

    def next(self, agent: Agent) -> 'Flow':
        self.agents.append(agent)
        return self

    def conditional(self, *conditions: When, default: Optional[Agent] = None) -> 'Flow':
        from tudi.conditional import ConditionalRunnable
        conditional_agent = ConditionalRunnable(list(conditions), default)
        self.agents.append(conditional_agent)
        return self

    def run(self, input_data: Any) -> Any:
        result = input_data
        for agent in self.agents:
            result = agent.run(result)
        return result