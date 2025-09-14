from src.tools.wolfram_alpha import create_wolfram_alpha_tool
from langchain_deepseek import ChatDeepSeek

from pathlib import Path
from dotenv import load_dotenv

import os

# 在当前文件的父目录下找到 .env 文件
load_dotenv(dotenv_path=Path(__file__).resolve().parent / "src" / ".env", override=False)

llm = ChatDeepSeek(
    model="deepseek-chat", 
    api_key=os.getenv("DEEPSEEK_API_KEY"), 
    base_url=os.getenv("DEEPSEEK_API_BASE")
    )

tool = create_wolfram_alpha_tool()

llm.bind_tools([tool])

result = llm.invoke("solve x^2 + 2x + 1 = 0")
print(result)