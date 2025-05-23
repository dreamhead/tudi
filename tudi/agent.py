from types import SimpleNamespace
from typing import Any, Callable, List, Optional, Type, TypeVar

from langchain.agents import AgentExecutor, create_react_agent
from langchain.agents.output_parsers import ReActJsonSingleInputOutputParser
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import BaseOutputParser, PydanticOutputParser, StrOutputParser
from langchain_core.prompts import (
    BasePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.tools import render_text_description_and_args
from pydantic import BaseModel

from tudi.output_parsers import ThinkTagRemoverOutputParser

from .base import Task

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)


class Agent(Task):
    def __init__(self,
                 name: str,
                 model: BaseChatModel,
                 prompt_template: Optional[str] = None,
                 input_type: Optional[Type[InputT]] = None,
                 output_type: Optional[Type[OutputT]] = None,
                 tools: Optional[List[Callable]] = None):
        if input_type and not prompt_template:
            raise ValueError("prompt_template must be provided when input_type is set")

        self.name = name
        self.model = model
        self.prompt_template = prompt_template
        self._input_type = input_type
        self._output_type = output_type
        base_parser = PydanticOutputParser(pydantic_object=output_type) if output_type else StrOutputParser()
        self.output_parser = ThinkTagRemoverOutputParser(parser=base_parser) if base_parser else None
        self.tools = tools or []
        self._prompt_template = self._init_prompt_template(prompt_template, tools, self.output_parser)
        self._runnable = self._init_runnable(model, tools, self._prompt_template)
        self._result_template = self._init_result_template()

    @property
    def input_type(self) -> Type[InputT]:
        return self._input_type

    @property
    def output_type(self) -> Type[OutputT]:
        return self._output_type

    def _init_prompt_template(self, prompt_template, tools, output_parser) -> BasePromptTemplate:
        if not tools:
            return self._create_template(prompt_template, output_parser)

        return self._create_agent_prompt()

    def _init_result_template(self) -> Optional[PromptTemplate]:
        if not self.output_type:
            return None

        from tudi.prompts import TYPED_RESULT_PROMPT
        return PromptTemplate.from_template(
            template=TYPED_RESULT_PROMPT,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()}
        )

    def _init_runnable(self, model, tools, prompt_template) -> Runnable:
        if not tools:
            return model

        agent = create_react_agent(model, tools, prompt_template,
                                   tools_renderer=render_text_description_and_args,
                                   output_parser=ReActJsonSingleInputOutputParser())
        return AgentExecutor(agent=agent, tools=tools, verbose=True)

    def run(self, input_data: Any) -> Any:
        self._validate_input(input_data)
        if not self.tools:
            return self.process_without_tools(input_data)

        return self._process_with_tools(input_data)

    def _validate_input(self, input_data: Any) -> None:
        if self._input_type and not isinstance(input_data, self._input_type):
            raise TypeError(f"Input must be of type {self._input_type.__name__}")

    def process_without_tools(self, input_data) -> Any:
        template_vars = self._prepare_template_vars(input_data)
        formated = self._prompt_template.format(**template_vars)
        chain = self._runnable | self._get_output_parser()
        return chain.invoke(formated)

    def _process_with_tools(self, input_data: Any) -> Any:
        chain = {"input": RunnablePassthrough()} | self._runnable | (lambda x: x["output"])
        result = chain.invoke({"input": self._as_input(input_data)})
        return self.return_as_tool_output(result)

    def return_as_tool_output(self, result) -> Any:
        if not self.output_type:
            return str(result)

        result_chain = self._result_template | self.model | self.output_parser
        final_result = result_chain.invoke({"input": result})
        return final_result

    def _get_output_parser(self) -> BaseOutputParser:
        return self.output_parser if self.output_parser else ThinkTagRemoverOutputParser(StrOutputParser())

    def _create_agent_prompt(self) -> ChatPromptTemplate:
        from tudi.prompts import AGENT_PROMPT
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(AGENT_PROMPT),
            HumanMessagePromptTemplate.from_template('''{input}

        {agent_scratchpad}''')])

    def _as_input(self, input_data: Any) -> str:
        if self.prompt_template:
            template_vars = self._prepare_template_vars(input_data)
            return self.prompt_template.format(**template_vars)

        return str(input_data)

    def _create_template(self, prompt_template: str, output_parser: BaseOutputParser) -> PromptTemplate:
        if prompt_template and output_parser:
            return PromptTemplate(
                template=f"{prompt_template}\n{{format_instructions}}",
                partial_variables={"format_instructions": output_parser.get_format_instructions()}
            )

        if prompt_template:
            return PromptTemplate.from_template(prompt_template)

        return PromptTemplate.from_template("{input}")

    def _prepare_template_vars(self, input_data: Any) -> dict:
        if isinstance(input_data, BaseModel):
            return {"arg": SimpleNamespace(**input_data.model_dump())}
        return {"input": input_data}
