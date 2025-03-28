from typing import Any, Type, TypeVar

from pydantic import BaseModel

from tudi.base import Statement, Task

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)

class NextStatement(Statement):
    def __init__(self, runnable: Task):
        self.runnable = runnable
        self._input_type = runnable.input_type

    @property
    def input_type(self) -> Type[InputT]:
        return self._input_type

    @property
    def output_type(self) -> Type[OutputT]:
        return self.runnable.output_type

    def run(self, input_data: Any) -> Any:
        return self.runnable.run(input_data)