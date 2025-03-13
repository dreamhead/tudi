import os

import pytest
from langchain_ollama import ChatOllama


@pytest.fixture
def model():
    model_name = os.getenv("TUDI_TEST_MODEL", "qwen2.5")
    return ChatOllama(model=model_name)