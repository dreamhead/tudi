# Tudi

[English](README.md) | 中文

Tudi 是一个轻量级 Agent 框架，它提供了一种简单而强大的方式来构建和使用 AI Agent。

## 特性

- **简单直观的 API**：通过简洁的 API 设计，让你能够快速创建和配置 Agent
- **类型安全**：支持输入输出的类型定义，提供类型安全的数据处理
- **工具集成**：轻松集成和使用自定义工具，扩展 Agent 的能力
- **灵活的提示模板**：支持自定义提示模板，实现更精确的 Agent 控制
- **易于集成**：与 LangChain 等主流框架无缝集成，提供更多扩展可能

## 快速开始

### 基本使用

```python
from tudi import Agent
from langchain_ollama import ChatOllama

# 创建一个基本的 Agent
agent = Agent(
    name="test_agent",
    model=ChatOllama(model="qwen2.5")
)

# 运行 Agent
result = agent.run("What is 2 + 2? Answer the result directly")
print(result)  # 输出: 4
```

### 类型安全

```python
from pydantic import BaseModel

class Query(BaseModel):
    question: str

class Answer(BaseModel):
    result: str

# 创建带类型的 Agent
agent = Agent(
    name="test_agent",
    model=ChatOllama(model="qwen2.5"),
    prompt_template="Answer the following question:{arg.question}",
    input_type=Query,
    output_type=Answer
)

# 使用类型安全的方式运行
result = agent.run(Query(question="What is 2 + 2?"))
print(result.result)  # 输出类型安全的结果
```

### 工具集成

```python
from langchain_core.tools import tool

@tool
def calculate(what: str) -> float:
    """运行计算并返回结果"""
    return eval(what)

@tool
def ask_fruit_unit_price(fruit: str) -> str:
    """获取水果单价"""
    if fruit.casefold() == "apple":
        return "Apple unit price is 10/kg"
    return "Unknown fruit"

# 创建带工具的 Agent
agent = Agent(
    name="test_agent",
    model=ChatOllama(model="qwen2.5"),
    tools=[calculate, ask_fruit_unit_price]
)

# 使用工具解决复杂问题
result = agent.run("What is the total price of 3 kg of apple?")
print(result)  # 输出: 30
```

### 流程控制 API

Flow API 允许你通过链接多个 Agent 来构建复杂的工作流。它提供了两个关键方法：

- **next**：按顺序链接 Agent 以创建线性工作流。每个 Agent 的输出将成为下一个 Agent 的输入。
- **conditional**：基于 Agent 的输出创建分支逻辑。可以根据条件选择不同的下游 Agent。

以下示例展示了顺序流和条件分支流的使用：

```python
from pydantic import BaseModel
from tudi import Agent, Flow, when

# 定义类型以确保类型安全
class WeatherQuery(BaseModel):
    city: str

class WeatherInfo(BaseModel):
    temperature: float
    condition: str

class ClothingAdvice(BaseModel):
    suggestion: str

# 创建天气查询 agent
weather_agent = Agent(
    name="weather_agent",
    model=ChatOllama(model="qwen2.5"),
    prompt_template="获取{arg.city}的天气",
    input_type=WeatherQuery,
    output_type=WeatherInfo
)

# 创建着装建议 agent
clothing_agent = Agent(
    name="clothing_agent",
    model=ChatOllama(model="qwen2.5"),
    prompt_template="根据气温{arg.temperature}和天气状况{arg.condition}给出着装建议",
    input_type=WeatherInfo,
    output_type=ClothingAdvice
)

# 创建极端天气着装建议 agent
extreme_clothing_agent = Agent(
    name="extreme_clothing_agent",
    model=ChatOllama(model="qwen2.5"),
    prompt_template="针对极端天气（气温{arg.temperature}°C，天气状况{arg.condition}）给出防护性着装建议",
    input_type=WeatherInfo,
    output_type=ClothingAdvice
)

# 构建顺序流
flow = Flow.start(weather_agent).next(clothing_agent)

# 运行顺序流
result = flow.run(WeatherQuery(city="北京"))
print(result.suggestion)  # 输出: 基本着装建议

# 构建带条件分支的工作流
flow_with_condition = Flow.start(weather_agent).conditional(
    when(lambda x: x.temperature > 35 or x.temperature < 0).then(extreme_clothing_agent),
    default=clothing_agent
)

# 运行条件分支流
result = flow_with_condition.run(WeatherQuery(city="北京"))
print(result.suggestion)  # 输出: 基于天气状况的着装建议
```


## 运行测试

### 环境准备

- 安装并运行 [Ollama](https://ollama.ai)
- 选择以下任一方式配置模型：
  1. 安装 qwen2.5 模型
  2. 安装自定义模型并配置 TUDI_TEST_MODEL 环境变量

```bash
# 选项一：安装 qwen2.5 模型
ollama pull qwen2.5

# 选项二：安装自定义模型并设置环境变量
ollama pull your-model-name
export TUDI_TEST_MODEL=your-model-name

# 运行测试
poetry run pytest
```

## 许可证

项目采用 [MIT许可证](LICENSE.txt)，详情请参阅许可证文件。