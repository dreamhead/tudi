from langchain_core.tools import tool
from pydantic import BaseModel

from tudi import Agent, Flow

from .util import normalize_string


class WeatherReport(BaseModel):
    city: str
    weather: str


@tool
def get_weather(city: str) -> str:
    """Gets the weather for a given city"""
    return f"forecast for {normalize_string(city)} is sunny"

@tool
def get_dressing_advice(weather: str) -> str:
    """Gets dressing advice based on weather"""
    if normalize_string(weather) == "sunny":
        return f"dressing code for {normalize_string(weather)} is Business Casual"

    return f"dressing code for {normalize_string(weather)} is Formal Wear"

class TestFlow:
    def test_flow_with_next(self, model):
        weather_agent = Agent(
            name="weather agent",
            model=model,
            prompt_template="Answer the weather report: {input}",
            tools=[get_weather]
        )

        dressing_agent = Agent(
            name="dressing agent",
            model=model,
            prompt_template="Give the dressing advice based on weather report: {input}",
            tools=[get_dressing_advice]
        )

        flow = Flow.start(weather_agent).next(dressing_agent)
        result = flow.run("Beijing")
        assert "casual" in result.lower()

    def test_flow_with_type(self, model):
        weather_agent = Agent(
            name="weather agent",
            model=model,
            prompt_template="Answer the weather report: {input}",
            tools=[get_weather],
            output_type=WeatherReport
        )

        dressing_agent = Agent(
            name="dressing agent",
            model=model,
            prompt_template="Give the dressing advice based on weather: {arg.weather}",
            tools=[get_dressing_advice],
            input_type=WeatherReport
        )

        flow = Flow.start(weather_agent).next(dressing_agent)
        result = flow.run("Beijing")
        assert "casual" in result.lower()

    def test_flow_with_map(self, model):
        weather_agent = Agent(
            name="weather agent",
            model=model,
            prompt_template="Answer the weather report: {input}",
            tools=[get_weather]
        )

        dressing_agent = Agent(
            name="dressing agent",
            model=model,
            prompt_template="Give the dressing advice based on weather report: {input}",
            tools=[get_dressing_advice]
        )

        def extract_weather(input_str: str) -> str:
            return input_str.split("is")[-1].strip()

        flow = (Flow.start(weather_agent)
                .map(extract_weather)
                .next(dressing_agent))
        result = flow.run("Beijing")
        assert "casual" in result.lower()