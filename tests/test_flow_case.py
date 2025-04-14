import pytest
from langchain_core.tools import tool
from pydantic import BaseModel

from tudi import Agent, Flow, default, when

from .util import normalize_string


class WeatherReport(BaseModel):
    city: str
    degree: int


class DressingAdvice(BaseModel):
    suggestion: str


class CustomOutput(BaseModel):
    message: str
    temperature: int


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
def get_dressing_advice(degree: int) -> str:
    """Gets dressing advice based on degree"""
    if degree > 30:
        return f"dressing code for {degree} is Athleisure"
    elif degree > 25:
        return f"dressing code for {degree} is Resort Casual"
    else:
        return f"dressing code for {degree} is Smart Casual"


class TestFlowCase:
    def test_case_flow(self, model):
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
            prompt_template="Just give a summer dressing code for {arg.degree}°C, Do NOT explain to much",
            model=model,
            tools=[get_dressing_advice]
        )

        winter_agent = Agent(
            name="winter_dressing",
            input_type=WeatherReport,
            output_type=DressingAdvice,
            prompt_template="Just give a winter dressing code for {arg.degree}°C, Do NOT explain to much",
            model=model,
            tools=[get_dressing_advice]
        )

        default_agent = Agent(
            name="default_dressing",
            input_type=WeatherReport,
            output_type=DressingAdvice,
            prompt_template="Just give a default dressing code for {arg.degree}°C, Do NOT explain to much",
            model=model,
            tools=[get_dressing_advice]
        )

        flow = (Flow.start(weather_agent)
        .case(
            when(lambda weather: int(weather.degree) > 30).then(summer_agent),
            when(lambda weather: int(weather.degree) < 10).then(winter_agent),
            default(default_agent)
        ))

        result = flow.run("guangzhou")
        assert "athleisure" in result.suggestion.lower()

        result = flow.run("beijing")
        assert "casual" in result.suggestion.lower()

    def test_case_flow_with_map(self, model):
        weather_agent = Agent(
            name="weather agent",
            model=model,
            prompt_template="Answer the weather report: {input}",
            tools=[get_weather]
        )

        summer_agent = Agent(
            name="summer_dressing",
            model=model,
            prompt_template="Just give a summer dressing code for {input}°C, Do NOT explain to much",
            tools=[get_dressing_advice],
            output_type=DressingAdvice
        )

        winter_agent = Agent(
            name="winter_dressing",
            model=model,
            prompt_template="Just give a winter dressing code for {input}°C, Do NOT explain to much",
            tools=[get_dressing_advice],
            output_type=DressingAdvice
        )

        default_agent = Agent(
            name="default_dressing",
            model=model,
            prompt_template="Just give a default dressing code for {input}°C, Do NOT explain to much",
            tools=[get_dressing_advice],
            output_type=DressingAdvice
        )

        def extract_degree(weather_str: str) -> int:
            # Extract the temperature value from the weather report string
            import re
            # Find any number followed by °C in the string
            match = re.search(r'(\d+)\s*(?:°C|degrees\s+Celsius)\.?', weather_str)
            if match:
                return int(match.group(1))
            # Fallback to the original method if no match is found
            degree_str = weather_str.split("is")[-1].strip()
            return int(degree_str.replace("°C", "").replace("degrees Celsius", "").rstrip('.'))

        flow = (Flow.start(weather_agent)
        .map(extract_degree)
        .case(
            when(lambda degree: degree > 30).then(summer_agent),
            when(lambda degree: degree < 10).then(winter_agent),
            default(default_agent)
        ))

        result = flow.run("guangzhou")
        assert "athleisure" in result.suggestion.lower()

        result = flow.run("beijing")
        assert "casual" in result.suggestion.lower()

    def test_case_flow_with_to_output(self, model):
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
            prompt_template="Just give a summer dressing code for {arg.degree}°C, Do NOT explain to much",
            model=model,
            tools=[get_dressing_advice]
        )

        winter_agent = Agent(
            name="winter_dressing",
            input_type=WeatherReport,
            output_type=DressingAdvice,
            prompt_template="Just give a winter dressing code for {arg.degree}°C, Do NOT explain to much",
            model=model,
            tools=[get_dressing_advice]
        )

        default_agent = Agent(
            name="default_dressing",
            input_type=WeatherReport,
            output_type=DressingAdvice,
            prompt_template="Just give a default dressing code for {arg.degree}°C, Do NOT explain to much",
            model=model,
            tools=[get_dressing_advice]
        )

        flow = (Flow.start(weather_agent)
        .case(
            when(lambda weather: int(weather.degree) > 30).then(summer_agent).to_output(
                lambda advice: CustomOutput(message=advice.suggestion, temperature=35)
            ),
            when(lambda weather: int(weather.degree) < 10).then(winter_agent).to_output(
                lambda advice: CustomOutput(message=advice.suggestion, temperature=5)
            ),
            default(default_agent).to_output(
                lambda advice: CustomOutput(message=advice.suggestion, temperature=25)
            ),
            output_type=CustomOutput
        ))

        result = flow.run("guangzhou")
        assert isinstance(result, CustomOutput)
        assert "athleisure" in result.message.lower()
        assert result.temperature == 35

        # 测试默认分支不使用to_output，但需要符合output_type
        flow = (Flow.start(weather_agent)
        .case(
            when(lambda weather: int(weather.degree) > 40).then(summer_agent).to_output(
                lambda advice: CustomOutput(message=advice.suggestion, temperature=45)
            ),
            when(lambda weather: int(weather.degree) < 10).then(winter_agent).to_output(
                lambda advice: CustomOutput(message=advice.suggestion, temperature=5)
            ),
            default(default_agent).to_output(
                lambda advice: CustomOutput(message=advice.suggestion, temperature=25)
            ),
            output_type=CustomOutput
        ))

        result = flow.run("beijing")
        assert isinstance(result, CustomOutput)
        assert "casual" in result.message.lower()

    def test_case_flow_with_type_validation(self, model):
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

        # 测试类型不匹配的情况
        with pytest.raises(TypeError, match="Type mismatch"):
            flow = (Flow.start(weather_agent)
            .case(
                when(lambda weather: int(weather.degree) > 30).then(summer_agent),
                output_type=CustomOutput  # 指定了不匹配的输出类型
            ))
            flow.run("guangzhou")
