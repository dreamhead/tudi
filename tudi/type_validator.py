from tudi.agent import Agent
from tudi.base import BaseRunnable


def validate_type_compatibility(last_runnable: BaseRunnable, next_runnable: BaseRunnable) -> None:
    if last_runnable.output_type and next_runnable.input_type:
        if last_runnable.output_type != next_runnable.input_type:
            last_name = last_runnable.name if isinstance(last_runnable, Agent) else type(last_runnable).__name__
            next_name = next_runnable.name if isinstance(next_runnable, Agent) else type(next_runnable).__name__
            error_msg = f"""Type mismatch:
  {last_name} output type: {last_runnable.output_type.__name__}
  {next_name} input type: {next_runnable.input_type.__name__}"""
            raise TypeError(error_msg)