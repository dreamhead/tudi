import pytest
from pydantic import BaseModel

from tudi import Agent, Flow, default


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
            
    def test_flow_case_branch_type_mismatch(self, model):
        from tudi import when
        
        # 创建一个输出类型为OutputType的Agent
        first_agent = Agent(
            name="first agent",
            model=model,
            prompt_template="Process the input: {input}",
            output_type=OutputType
        )
        
        # 创建两个具有不同输出类型的Agent
        branch_agent1 = Agent(
            name="branch agent 1",
            model=model,
            prompt_template="Process the input: {arg.result}",
            input_type=OutputType,
            output_type=OutputType
        )
        
        branch_agent2 = Agent(
            name="branch agent 2",
            model=model,
            prompt_template="Process the input: {arg.result}",
            input_type=OutputType,
            output_type=DifferentType
        )
        
        # 验证当case分支中的不同Agent返回类型不一致时会抛出异常
        with pytest.raises(TypeError, match="Type mismatch"):
            Flow.start(first_agent).case(
                when(lambda x: x.result == "condition1").then(branch_agent1),
                when(lambda x: x.result == "condition2").then(branch_agent2)
            )
    
    def test_flow_case_specified_output_type_mismatch(self, model):
        from tudi import when
        
        # 创建一个输出类型为OutputType的Agent
        first_agent = Agent(
            name="first agent",
            model=model,
            prompt_template="Process the input: {input}",
            output_type=OutputType
        )
        
        # 创建两个具有不同输出类型的Agent
        branch_agent = Agent(
            name="branch agent",
            model=model,
            prompt_template="Process the input: {arg.result}",
            input_type=OutputType,
            output_type=OutputType
        )
        
        default_agent = Agent(
            name="default agent",
            model=model,
            prompt_template="Process the input: {arg.result}",
            input_type=OutputType,
            output_type=DifferentType
        )
        
        # 验证当指定output_type与分支输出类型不匹配时会抛出异常
        with pytest.raises(TypeError, match="Type mismatch in case branches"):
            Flow.start(first_agent).case(
                when(lambda x: x.result == "condition").then(branch_agent),
                output_type=DifferentType
            )
        
        # 验证当指定output_type与默认分支输出类型不匹配时会抛出异常
        with pytest.raises(TypeError, match="Type mismatch in case branches"):
            Flow.start(first_agent).case(
                when(lambda x: x.result == "condition").then(branch_agent),
                default(default_agent),
                output_type=OutputType
            )