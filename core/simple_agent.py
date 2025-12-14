# 思考 行动 观察
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
os.getenv("DEEPSEEK_API_KEY")
os.getenv("GEMINI_API_KEY")
logger.info(f'密钥是: {os.getenv("DEEPSEEK_API_KEY")} ')

logger.info('this is the test result')

# 1智能体如何构造: agent智能体 = llm大语言模型 + toolcall工具函数 + system_prompt系统提示词 
# 2智能体如何运行: 创建一个引擎 多轮调用agent 调用工具函数 添加错误处理
# 3智能体如何交互: 启动智能体 通过提示词得到输出