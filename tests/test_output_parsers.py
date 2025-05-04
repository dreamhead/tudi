import unittest

from langchain_core.output_parsers import StrOutputParser

from tudi.output_parsers import ThinkTagRemoverOutputParser


class TestThinkTagRemoverOutputParser(unittest.TestCase):
    def test_remove_think_tags(self):
        # 创建一个基础的StrOutputParser
        base_parser = StrOutputParser()
        # 使用ThinkTagRemoverOutputParser包装它
        parser = ThinkTagRemoverOutputParser(parser=base_parser)
        
        # 测试包含<think>标签的文本
        text_with_think_tags = """<think>
这是一些思考内容，应该被移除
</think>

实际输出内容"""
        
        # 解析文本
        result = parser.parse(text_with_think_tags)
        
        # 验证结果不包含<think>标签内容
        self.assertEqual(result, "实际输出内容")
        
    def test_remove_multiple_think_tags(self):
        # 创建一个基础的StrOutputParser
        base_parser = StrOutputParser()
        # 使用ThinkTagRemoverOutputParser包装它
        parser = ThinkTagRemoverOutputParser(parser=base_parser)
        
        # 测试包含多个<think>标签的文本
        text_with_multiple_think_tags = """<think>第一个思考</think>
实际内容1
<think>
多行
思考
</think>
实际内容2"""
        
        # 解析文本
        result = parser.parse(text_with_multiple_think_tags)
        
        # 验证结果不包含<think>标签内容
        self.assertEqual(result, "实际内容1\n实际内容2")
        
    def test_text_without_think_tags(self):
        # 创建一个基础的StrOutputParser
        base_parser = StrOutputParser()
        # 使用ThinkTagRemoverOutputParser包装它
        parser = ThinkTagRemoverOutputParser(parser=base_parser)
        
        # 测试不包含<think>标签的文本
        text_without_think_tags = "这是一个没有think标签的普通文本"
        
        # 解析文本
        result = parser.parse(text_without_think_tags)
        
        # 验证结果与输入相同
        self.assertEqual(result, text_without_think_tags)