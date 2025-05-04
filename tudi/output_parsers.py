import re
from typing import Any, Optional

from langchain_core.output_parsers import BaseOutputParser, StrOutputParser


class ThinkTagRemoverOutputParser(BaseOutputParser):
    """OutputParser装饰器，用于去除<think>标签并将清理后的文本传递给原始OutputParser进行解析。
    
    这个OutputParser主要用于处理Qwen 3模型返回的<think>标签，这些标签会导致解析错误。
    它会先去除输入中的<think>...</think>标签内容，然后将清理后的文本传递给原始的OutputParser进行解析。
    """

    parser: Optional[BaseOutputParser] = None
        
    def parse(self, text: str) -> Any:
        """解析文本，先去除<think>标签，然后使用原始parser解析。
        
        Args:
            text: 输入文本，可能包含<think>标签
            
        Returns:
            解析后的结果
        """
        # 去除<think>...</think>标签内容
        cleaned_text = self._remove_think_tags(text)
        # 使用原始parser解析清理后的文本
        if self.parser is not None:
            return self.parser.parse(cleaned_text)
        return cleaned_text
    
    def _remove_think_tags(self, text: str) -> str:
        """去除文本中的<think>...</think>标签内容。
        
        Args:
            text: 输入文本，可能包含<think>标签
            
        Returns:
            清理后的文本
        """
        # 使用正则表达式去除<think>...</think>标签内容
        pattern = r'<think>.*?</think>'
        cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
        # 移除多余的空行
        cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
        return cleaned_text.strip()
    
    def get_format_instructions(self) -> str:
        """获取格式说明。
        
        Returns:
            原始parser的格式说明
        """
        if self.parser is not None and not isinstance(self.parser, StrOutputParser):
            return self.parser.get_format_instructions()
        return ""