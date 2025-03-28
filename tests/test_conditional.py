from langchain_core.tools import tool
from pydantic import BaseModel

from tudi import Agent, Flow, when

from .util import normalize_string


class WeatherReport(BaseModel):
    city: str
    degree: int


class DressingAdvice(BaseModel):
    suggestion: str


@tool
def get_weather(city: str) -> str:
    """Gets the weather for a given city"""
    arg = normalize_string(city)
    if arg == 'beijing':
        return f"the weather of {arg} is 24°C"

    if arg == 'guangzhou':
        return f"the weather of {arg} is 35°C"

    return f"the weather of {arg} is 30°C"


@tool
def get_dressing_advice(degree: str) -> str:
    """Gets dressing advice based on degree"""
    degree = int(normalize_string(degree))
    if degree > 30:
        return f"dressing code for {degree} is Athleisure"
    elif degree > 25:
        return f"dressing code for {degree} is Resort Casual"
    else:
        return f"dressing code for {degree} is Smart Casual"


class TestConditional:
    def test_conditional_flow(self, model):
        weather_agent = Agent(
            name="weather agent",
            model=model,
            prompt_template="Answer the weather report: {input}",
            tools=[get_weather],
            output_type=WeatherReport
        )

        summer_agent = Agent(
            name="summer_dressing",
            input_type=WeatherReport,
            output_type=DressingAdvice,
            prompt_template="Suggest summer clothes for {arg.degree}°C",
            model=model,
            tools=[get_dressing_advice]
        )

        winter_agent = Agent(
            name="winter_dressing",
            input_type=WeatherReport,
            output_type=DressingAdvice,
            prompt_template="Suggest winter clothes for {arg.degree}°C",
            model=model,
            tools=[get_dressing_advice]
        )

        default_agent = Agent(
            name="default_dressing",
            input_type=WeatherReport,
            output_type=DressingAdvice,
            prompt_template="Default clothes for {arg.degree}°C",
            model=model,
            tools=[get_dressing_advice]
        )

        flow = Flow.start(weather_agent).conditional(
            when(lambda weather: int(weather.degree) > 30).then(summer_agent),
            when(lambda weather: int(weather.degree) < 10).then(winter_agent),
            default=default_agent
        )

        result = flow.run("guangzhou")
        assert "athleisure" in result.suggestion.lower()

        result = flow.run("beijing")
        assert "casual" in result.suggestion.lower()

    def test_conditional_flow_with_map(self, model):
        weather_agent = Agent(
            name="weather agent",
            model=model,
            prompt_template="Answer the weather report: {input}",
            tools=[get_weather]
        )

        summer_agent = Agent(
            name="summer_dressing",
            model=model,
            prompt_template="Suggest summer clothes for {input}°C",
            tools=[get_dressing_advice],
            output_type=DressingAdvice
        )

        winter_agent = Agent(
            name="winter_dressing",
            model=model,
            prompt_template="Suggest winter clothes for {input}°C",
            tools=[get_dressing_advice],
            output_type=DressingAdvice
        )

        default_agent = Agent(
            name="default_dressing",
            model=model,
            prompt_template="Default clothes for {input}°C",
            tools=[get_dressing_advice],
            output_type=DressingAdvice
        )

        def extract_degree(weather_str: str) -> int:
            # Extract the temperature value from the weather report string
            import re
            # Find any number followed by °C in the string
            match = re.search(r'(\d+)\s*°C', weather_str)
            if match:
                return int(match.group(1))
            # Fallback to the original method if no match is found
            degree_str = weather_str.split("is")[-1].strip()
            return int(degree_str.replace("°C", "").rstrip('.'))

        flow = (Flow.start(weather_agent)
        .map(extract_degree)
        .conditional(
            when(lambda degree: degree > 30).then(summer_agent),
            when(lambda degree: degree < 10).then(winter_agent),
            default=default_agent
        ))

        result = flow.run("guangzhou")
        assert "athleisure" in result.suggestion.lower()

        result = flow.run("beijing")
        assert "casual" in result.suggestion.lower()
