from langchain_core.tools import tool

from tudi import Agent

from .util import normalize_string


@tool
def calculate(what: str) -> float:
    """Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary"""
    return eval(normalize_string(what))

@tool
def ask_fruit_unit_price(fruit: str) -> str:
    """Asks the user for the price of a fruit"""
    normalized_fruit = normalize_string(fruit)
    if normalized_fruit == "apple":
        return "Apple unit price is 10/kg"
    elif normalized_fruit == "banana":
        return "Banana unit price is 6/kg"
    else:
        return "{} unit price is 20/kg".format(fruit)

class TestAgentMultiTools:

    def test_agent_with_multi_tools(self, model):
        agent = Agent(
            name="test_agent", 
            model=model,
            tools=[calculate, ask_fruit_unit_price]
        )
        result = agent.run("What is the total price of 3 kg of apple and 2 kg of banana?")
        assert isinstance(result, str)
        assert "42" in result  # 3 * 10 + 2 * 6 = 42