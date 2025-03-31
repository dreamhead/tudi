import pytest
from pydantic import BaseModel

from tudi import Agent, Flow


class InputType(BaseModel):
    name: str


class OutputType(BaseModel):
    result: str


class DifferentType(BaseModel):
    value: int


class TestFlowTypeCheck:
    def test_flow_type_mismatch(self, model):
        first_agent = Agent(
            name="first agent",
            model=model,
            prompt_template="Process the input: {input}",
            output_type=OutputType
        )

        second_agent = Agent(
            name="second agent",
            model=model,
            prompt_template="Process the input: {arg.name}",
            input_type=InputType
        )

        with pytest.raises(TypeError, match="Type mismatch"):
            Flow.start(first_agent).next(second_agent)

    def test_flow_case_type_mismatch(self, model):
        from tudi import when

        first_agent = Agent(
            name="first agent",
            model=model,
            prompt_template="Process the input: {input}",
            output_type=OutputType
        )

        second_agent = Agent(
            name="second agent",
            model=model,
            prompt_template="Process the input: {arg.name}",
            input_type=InputType
        )

        with pytest.raises(TypeError, match="Type mismatch"):
            Flow.start(first_agent).case(
                when(lambda x: True).then(second_agent)
            )