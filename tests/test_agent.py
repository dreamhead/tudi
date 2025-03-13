from pydantic import BaseModel

from tudi import Agent


class Query(BaseModel):
    question: str

class Answer(BaseModel):
    result: str

class TestAgent:

    def test_agent_run(self, model):
        agent = Agent(
            name="test_agent", 
            model=model
        )
        result = agent.run("What is 2 + 2? Answer the result directly")
        assert result is not None
        assert "4" in result

    def test_agent_run_with_type(self, model):
        agent = Agent(
            name="test_agent", 
            model=model,
            prompt_template="Answer the following question:{arg.question}",
            input_type=Query,
            output_type=Answer
        )
        result = agent.run(Query(question="What is 2 + 2? Answer the result directly"))
        assert isinstance(result, Answer)
        assert result.result is not None
        assert "4" in result.result

    def test_agent_run_with_prompt_no_output_type(self, model):
        agent = Agent(
            name="test_agent", 
            model=model,
            prompt_template="Answer the following question:{arg.question}",
            input_type=Query
        )
        result = agent.run(Query(question="What is 2 + 2? Answer the result directly"))
        assert isinstance(result, str)
        assert len(result) > 0
        assert "4" in result

    def test_agent_run_with_output_type_no_input_type(self, model):
        agent = Agent(
            name="test_agent", 
            model=model,
            prompt_template="Answer the following question: {input}",
            output_type=Answer
        )
        result = agent.run("What is 2 + 2? Answer the result directly")
        assert isinstance(result, Answer)
        assert result.result is not None
        assert "4" in result.result