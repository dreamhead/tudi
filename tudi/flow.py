from typing import Any, List

from tudi.agent import Agent


class Flow:
    def __init__(self, agent: Agent):
        self.agents: List[Agent] = [agent]

    @classmethod
    def start(cls, agent: Agent) -> 'Flow':
        return cls(agent)

    def next(self, agent: Agent) -> 'Flow':
        self.agents.append(agent)
        return self

    def run(self, input_data: Any) -> Any:
        result = input_data
        for agent in self.agents:
            result = agent.run(result)
        return result