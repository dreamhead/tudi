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
        self._validate_type_compatibility(agent)
        self.agents.append(agent)
        return self

    def conditional(self, *conditions: When, default: Optional[Agent] = None) -> 'Flow':
        from tudi.conditional import ConditionalRunnable
        for condition in conditions:
            if condition.agent:
                self._validate_type_compatibility(condition.agent)
        if default:
            self._validate_type_compatibility(default)
        conditional_agent = ConditionalRunnable(list(conditions), default)
        self.agents.append(conditional_agent)
        return self

    def _validate_type_compatibility(self, next_agent: Agent) -> None:
        if not self.agents:
            return

        last_agent = self.agents[-1]
        if not isinstance(last_agent, Agent):
            return

        if last_agent.output_type and next_agent.input_type:
            if last_agent.output_type != next_agent.input_type:
                error_msg = f"""Type mismatch:
  {last_agent.name} output type: {last_agent.output_type.__name__}
  {next_agent.name} input type: {next_agent.input_type.__name__}"""
                raise TypeError(error_msg)


    def run(self, input_data: Any) -> Any:
        result = input_data
        for agent in self.agents:
            result = agent.run(result)
        return result