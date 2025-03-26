from typing import Any


class BaseRunnable:
    def run(self, input_data: Any) -> Any:
        raise NotImplementedError()