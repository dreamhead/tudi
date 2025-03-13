from langchain_core.tools import tool

from tudi import Agent


@tool
def calculate(what: str) -> float:
    """Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary"""
    return eval(what)

class TestAgentTools:

    def test_agent_with_tools(self, model):
        agent = Agent(
            name="test_agent", 
            model=model,
            tools=[calculate]
        )
        result = agent.run("What is 2 + 2? Answer the result directly")
        assert isinstance(result, str)
        assert "4" in result

    def test_agent_with_tools_and_prompt(self, model):
        agent = Agent(
            name="test_agent", 
            model=model,
            prompt_template="Please calculate: {input}",
            tools=[calculate]
        )
        result = agent.run("What is 3 * 3? Answer the result directly")
        assert isinstance(result, str)
        assert "9" in result