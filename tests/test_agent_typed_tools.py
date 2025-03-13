from langchain_core.tools import tool
from pydantic import BaseModel

from tudi import Agent


class FruitQuery(BaseModel):
    fruit: str
    amount: float


class PriceResult(BaseModel):
    total: float


@tool
def calculate(what: str) -> float:
    """Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary"""
    return eval(what)


@tool
def ask_fruit_unit_price(fruit: str) -> str:
    """Asks the user for the price of a fruit"""
    if fruit.casefold() == "apple":
        return "Apple unit price is 10/kg"
    elif fruit.casefold() == "banana":
        return "Banana unit price is 6/kg"
    else:
        return "{} unit price is 20/kg".format(fruit)


class TestAgentTypedTools:
    def test_agent_with_typed_tools(self, model):
        agent = Agent(
            name="test_agent",
            model=model,
            tools=[calculate, ask_fruit_unit_price],
            output_type=PriceResult,
        )
        result = agent.run("What is the total price of 3 kg of apple and 2 kg of banana?")
        assert isinstance(result, PriceResult)
        assert result.total == 42

    def test_agent_with_typed_tools_and_prompt(self, model):
        agent = Agent(
            name="test_agent",
            model=model,
            prompt_template="Please calculate the price: {arg.amount} kg of {arg.fruit}",
            input_type=FruitQuery,
            output_type=PriceResult,
            tools=[calculate, ask_fruit_unit_price],
        )
        result = agent.run(FruitQuery(fruit="banana", amount=2.0))
        assert isinstance(result, PriceResult)
        assert result.total == 12  # 2 kg * 6/kg = 12
