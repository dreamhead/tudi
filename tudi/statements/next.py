from typing import Any, Callable, Type, TypeVar

from pydantic import BaseModel

from tudi.base import Statement, Task

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)

class NextStatement(Statement):
    def __init__(self, runnable: Task, map_input: Callable[[Any], Any]):
        self.runnable = runnable
        self.map_input = map_input
        self._input_type = runnable.input_type

    @property
    def input_type(self) -> Type[InputT]:
        return self._input_type

    @property
    def output_type(self) -> Type[OutputT]:
        return self.runnable.output_type

    def run(self, input_data: Any) -> Any:
        transformed_input = self.map_input(input_data)
        return self.runnable.run(transformed_input)