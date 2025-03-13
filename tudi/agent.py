from types import SimpleNamespace
from typing import Any, Callable, List, Optional, Type, TypeVar

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)


class Agent:
    def __init__(self,
                 name: str,
                 model: BaseChatModel,
                 prompt_template: Optional[str] = None,
                 input_type: Optional[Type[InputT]] = None,
                 output_type: Optional[Type[OutputT]] = None,
                 tools: Optional[List[Callable]] = None):
        self.name = name
        self.model = model
        self.prompt_template = prompt_template
        self.input_type = input_type
        self.output_type = output_type
        self.output_parser = JsonOutputParser(pydantic_object=output_type) if output_type else None
        self.tools = tools or []

    def run(self, input_data: Any) -> Any:
        self._validate_input(input_data)
        result = self._process_request(input_data)
        return self._process_output(result)

    def _validate_input(self, input_data: Any) -> None:
        if self.input_type and not isinstance(input_data, self.input_type):
            raise TypeError(f"Input must be of type {self.input_type.__name__}")

    def _process_request(self, input_data: Any) -> Any:
        if not self.tools:
            return self._process_without_tools(input_data)
        return self._process_with_tools(input_data)

    def _process_without_tools(self, input_data: Any) -> Any:
        prompt = self._prepare_prompt(input_data)
        response = self.model.invoke(prompt)
        return response.content

    def _process_with_tools(self, input_data: Any) -> Any:
        template_vars = self._prepare_template_vars(input_data)
        if self.prompt_template:
            template_vars["input"] = self._process_template(input_data)

        prompt = self._create_agent_prompt()
        if self.output_type:
            prompt.partial_variables["format_instructions"] = self.output_parser.get_format_instructions()
        agent = create_react_agent(self.model, self.tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=True)
        return agent_executor.invoke(template_vars)["output"]

    def _process_output(self, result: Any) -> Any:
        if not self.output_type:
            return result

        try:
            if isinstance(result, str):
                if self.output_parser:
                    parsed_result = self.output_parser.parse(result)
                    return self.output_type(**parsed_result)
                return self.output_type(result=result)
            return result
        except Exception:
            if isinstance(result, dict):
                return self.output_type(**result)
            return result

    def _prepare_prompt(self, input_data: Any) -> str:
        if self.prompt_template:
            return self._process_template(input_data)
        return str(input_data)

    def _create_agent_prompt(self) -> PromptTemplate:
        from tudi.prompts import AGENT_PROMPT
        final_answer_format = "the final answer to the original input question"
        if self.output_type:
            final_answer_format = self.output_parser.get_format_instructions()
        return PromptTemplate.from_template(AGENT_PROMPT).partial(final_answer_format=final_answer_format)

    def _process_template(self, input_data: Any) -> str:
        template_vars = self._prepare_template_vars(input_data)
        template = self._create_template(template_vars)
        return template.format(**template_vars)

    def _create_template(self, template_vars: dict) -> PromptTemplate:
        if self.output_parser:
            template_vars["format_instructions"] = self.output_parser.get_format_instructions()
            return PromptTemplate(
                template=f"{self.prompt_template}\n{{format_instructions}}",
                partial_variables={}
            )
        return PromptTemplate.from_template(self.prompt_template)

    def _prepare_template_vars(self, input_data: Any) -> dict:
        if isinstance(input_data, BaseModel):
            return {"arg": SimpleNamespace(**input_data.model_dump())}
        return {"input": input_data}
