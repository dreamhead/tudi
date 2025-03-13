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

## Running Tests

### Prerequisites

- Install and run [Ollama](https://ollama.ai)
- Choose one of the following methods to configure the model:
  1. Install qwen2.5 model
  2. Install your custom model and configure TUDI_TEST_MODEL environment variable

```bash
# Option 1: Install qwen2.5 model
ollama pull qwen2.5

# Option 2: Install your custom model and set environment variable
ollama pull your-model-name
export TUDI_TEST_MODEL=your-model-name

# Run tests
poetry run pytest
```

## License

This project is licensed under the [MIT License](LICENSE.txt). See the license file for details.