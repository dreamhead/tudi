from typing import Any, Callable, List, Optional, Type, TypeVar

from pydantic import BaseModel

from tudi.agent import Agent
from tudi.statements.case import When

from .base import Runnable, Statement, Task

InputT = TypeVar('InputT', bound=BaseModel)
OutputT = TypeVar('OutputT', bound=BaseModel)


class Flow(Task):
    def __init__(self, runnable: Task):
        super().__init__()
        self._tasks: List[Runnable] = [runnable]
        self._input_type = runnable.input_type

    def input_type(self) -> Type[InputT]:
        return self._input_type

    @property
    def output_type(self) -> Type[OutputT]:
        if not self._tasks:
            return None

        return self._tasks[-1].output_type

    @classmethod
    def start(cls, task: Task) -> 'Flow':
        return cls(task)

    def map(self, mapper: Callable[[Any], Any]) -> 'Flow':
        from tudi.statements import MapStatement
        task = MapStatement(mapper, self._tasks[-1].output_type)
        self._tasks.append(task)

        self._on_new_runnable(task)
        return self

    def next(self, task: Task) -> 'Flow':
        self._validate_type_compatibility(task)
        from tudi.statements import NextStatement
        task = NextStatement(task)
        self._tasks.append(task)
        # 添加钩子函数，设置前一个MapStatement的output_type
        self._on_new_runnable(task)
        return self

    def _create_case_statement(self, conditions: list[When],
                               output_type: Optional[Type] = None) -> Statement:
        from tudi.statements import CaseStatement
        for condition in conditions:
            if not condition.has_then():
                raise ValueError("Condition must have an agent set using 'then' method")
            condition.validate_type_compatibility(self._tasks[-1])

        # 检查所有分支的输出类型是否一致
        self._validate_case_branch_types(conditions, output_type)

        return CaseStatement(conditions, output_type)

    def _validate_case_branch_types(self, conditions: list[When],
                                    output_type: Optional[Type] = None) -> None:
        """检查所有分支的输出类型是否一致，如果指定了output_type，则所有分支的输出类型必须与之一致
        如果分支设置了to_output，则跳过该分支的类型检查
        """
        if not conditions:
            return

        # 确定基准输出类型：如果提供了output_type就使用它，否则使用第一个condition的output_type
        expected_type = output_type if output_type else conditions[0].output_type
        if not expected_type:
            return

        # 检查所有条件分支的输出类型是否与基准类型一致
        for i, condition in enumerate(conditions):
            # 如果设置了输出转换器，则跳过类型检查
            if condition.has_output_mapper():
                continue
                
            if condition.output_type != expected_type:
                type_mismatch_source = "specified output_type" if output_type else "Branch 0"
                error_msg = f"""Type mismatch in case branches:
  Expected output type ({type_mismatch_source}): {expected_type.__name__}
  Branch {i} output type: {condition.output_type.__name__}"""
                raise TypeError(error_msg)

    def case(self, *conditions: When,
             output_type: Optional[Type] = None) -> 'Flow':
        statement = self._create_case_statement(list(conditions), output_type)
        self._tasks.append(statement)
        # 添加钩子函数，设置前一个MapStatement的output_type
        self._on_new_runnable(statement)
        return self

    def _validate_type_compatibility(self, next_agent: Task) -> None:
        if not self._tasks:
            return

        last_agent = self._tasks[-1]
        if not isinstance(last_agent, Agent):
            return

        from tudi.type_validator import validate_type_compatibility
        validate_type_compatibility(last_agent, next_agent)

    def run(self, input_data: Any) -> Any:
        result = input_data
        for agent in self._tasks:
            result = agent.run(result)
        return result

    def _on_new_runnable(self, runnable: Runnable) -> None:
        self._set_previous_map_output_type()

    def _set_previous_map_output_type(self) -> None:
        """设置前一个MapStatement的output_type为当前任务的input_type"""
        if len(self._tasks) < 2:
            return

        prev_task = self._tasks[-2]
        current_task = self._tasks[-1]

        from tudi.statements import MapStatement
        if isinstance(prev_task, MapStatement) and prev_task.output_type is None:
            prev_task.output_type = current_task.input_type
