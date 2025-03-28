from abc import ABC, abstractmethod
from typing import Any, Type, TypeVar

from pydantic import BaseModel

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)

class Runnable(ABC):
    @abstractmethod
    def run(self, input_data: Any) -> Any:
        pass

    @property
    @abstractmethod
    def input_type(self) -> Type[OutputT]:
        pass

    @property
    @abstractmethod
    def output_type(self) -> Type[InputT]:
        pass


class Task(Runnable, ABC):
    pass

class Statement(Runnable, ABC):
    pass