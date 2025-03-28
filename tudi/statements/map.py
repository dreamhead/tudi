from typing import Any, Callable, Type, TypeVar

from pydantic import BaseModel

from tudi.base import Statement

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)


class MapStatement(Statement):
    def __init__(self, mapper: Callable[[Any], Any], input_type: Type[InputT]):
        self._mapper = mapper
        self._input_type = input_type
        self._output_type = None

    @property
    def input_type(self) -> Type[InputT]:
        return self._input_type

    @property
    def output_type(self) -> Type[OutputT]:
        return self._output_type

    @output_type.setter
    def output_type(self, value: Type[OutputT]):
        self._output_type = value

    def run(self, input_data: Any) -> Any:
        return self._mapper(input_data)

