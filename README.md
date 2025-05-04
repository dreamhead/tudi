# Tudi

[中文](README_CN.md) | English

Tudi is a lightweight Agent framework that provides a simple yet powerful way to build and use AI Agents.

## Features

- **Simple and Intuitive API**: Create and configure Agents quickly through a concise API design
- **Type Safety**: Support for input/output type definitions, providing type-safe data handling
- **Tool Integration**: Easily integrate and use custom tools to extend Agent capabilities
- **Flexible Prompt Templates**: Support custom prompt templates for more precise Agent control
- **Easy Integration**: Seamless integration with mainstream frameworks like LangChain for more extensibility

## Quick Start

### Basic Usage

```python
from tudi import Agent
from langchain_ollama import ChatOllama

# Create a basic Agent
agent = Agent(
    name="test_agent",
    model=ChatOllama(model="qwen2.5")
)

# Run the Agent
result = agent.run("What is 2 + 2? Answer the result directly")
print(result)  # Output: 4
```

### Type Safety

```python
from pydantic import BaseModel

class Query(BaseModel):
    question: str

class Answer(BaseModel):
    result: str

# Create a typed Agent
agent = Agent(
    name="test_agent",
    model=ChatOllama(model="qwen2.5"),
    prompt_template="Answer the following question:{arg.question}",
    input_type=Query,
    output_type=Answer
)

# Run with type safety
result = agent.run(Query(question="What is 2 + 2?"))
print(result.result)  # Output type-safe result
```

### Tool Integration

```python
from langchain_core.tools import tool

@tool
def calculate(what: str) -> float:
    """Run calculation and return the result"""
    return eval(what)

@tool
def ask_fruit_unit_price(fruit: str) -> str:
    """Get fruit unit price"""
    if fruit.casefold() == "apple":
        return "Apple unit price is 10/kg"
    return "Unknown fruit"

# Create an Agent with tools
agent = Agent(
    name="test_agent",
    model=ChatOllama(model="qwen2.5"),
    tools=[calculate, ask_fruit_unit_price]
)

# Solve complex problems using tools
result = agent.run("What is the total price of 3 kg of apple?")
print(result)  # Output: 30
```

### Flow API

Flow API enables you to build complex workflows by chaining multiple Agents together. It provides two key methods:

- **next**: Chain Agents sequentially to create a linear workflow. Each Agent's output becomes the input for the next Agent.
- **case**: Create branching logic based on the output of an Agent. Different downstream Agents can be selected based on conditions.

Here's an example that demonstrates both sequential and conditional flows:

```python
from pydantic import BaseModel
from tudi import Agent, Flow, when


# Define types for type safety
class WeatherQuery(BaseModel):
    city: str


class WeatherInfo(BaseModel):
    temperature: float
    condition: str


class ClothingAdvice(BaseModel):
    suggestion: str


# Create weather query agent
weather_agent = Agent(
    name="weather_agent",
    model=ChatOllama(model="qwen2.5"),
    prompt_template="Get weather for {arg.city}",
    input_type=WeatherQuery,
    output_type=WeatherInfo
)

# Create clothing advice agent
clothing_agent = Agent(
    name="clothing_agent",
    model=ChatOllama(model="qwen2.5"),
    prompt_template="Suggest clothing for temperature {arg.temperature} and condition {arg.condition}",
    input_type=WeatherInfo,
    output_type=ClothingAdvice
)

# Create alternative clothing agent for extreme weather
extreme_clothing_agent = Agent(
    name="extreme_clothing_agent",
    model=ChatOllama(model="qwen2.5"),
    prompt_template="Suggest protective clothing for extreme weather: {arg.temperature}°C, {arg.condition}",
    input_type=WeatherInfo,
    output_type=ClothingAdvice
)

# Build sequential flow
flow = Flow.start(weather_agent).next(clothing_agent)

# Run sequential flow
result = flow.run(WeatherQuery(city="New York"))
print(result.suggestion)  # Output: Basic clothing suggestion

# Build flow with conditional branching
flow_with_condition = Flow.start(weather_agent).case(
    when(lambda x: x.temperature > 35 or x.temperature < 0).then(extreme_clothing_agent),
    default=clothing_agent
)

# Run conditional flow
result = flow_with_condition.run(WeatherQuery(city="New York"))
print(result.suggestion)  # Output: Clothing suggestion based on weather conditions
```

## Running Tests

### Prerequisites

- Install and run [Ollama](https://ollama.ai)
- Choose one of the following methods to configure the model:
  1. Install qwen3 model
  2. Install your custom model and configure TUDI_TEST_MODEL environment variable

```bash
# Option 1: Install qwen2.5 model
ollama pull qwen3

# Option 2: Install your custom model and set environment variable
ollama pull your-model-name
export TUDI_TEST_MODEL=your-model-name

# Run tests
poetry run pytest
```

## License

This project is licensed under the [MIT License](LICENSE.txt). See the license file for details.