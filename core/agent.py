import os
import json
import httpx
from loguru import logger
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

load_dotenv()
API_KEY = os.getenv('DEEPSEEK_API_KEY')
MCP_URL = "http://localhost:8000"  # FastMCP 默认端口
logger.info("Using DeepSeek API Key")

# --- 1. 初始化 DeepSeek 模型 ---
llm = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=API_KEY,
    openai_api_base="https://api.deepseek.com/v1",
)

# --- 2. 定义 MCP 调用函数（不注册为 LangChain tool）---
def call_mcp_tool(tool_name: str, **kwargs) -> str:
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": tool_name,
        "params": kwargs
    }
    try:
        resp = httpx.post(MCP_URL, json=payload, timeout=30.0)
        resp.raise_for_status()
        result = resp.json()
        return result.get("result", "No result")
    except Exception as e:
        return f"Tool call failed: {e}"

# --- 3. 简单 Agent 逻辑：先让模型决定是否调用工具 ---
def run_agent(query: str) -> str:
    # 第一步：让模型判断是否需要工具 {}容易理解成变量
    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "你必须使用以下工具来回答用户问题，禁止凭记忆或猜测回答：\n"
            "- 获取当前时间：调用 get_current_time()\n"
            "- 查询网络信息：调用 web_search(query)\n"
            "你必须且只能输出一个 JSON 对象，格式如下：\n"
            '{{"use_tool": true, "tool_name": "工具名", "args": {{...}}}}\n'
            "不要输出任何其他文字、解释或 markdown。"
        )),
        ("human", query)
    ])
    chain = prompt | llm
    response = chain.invoke({"input": query})
    text = response.content.strip()

    # 尝试解析是否要调用工具
    try:
        import json
        if text.startswith("{") and text.endswith("}"):
            plan = json.loads(text)
            if plan.get("use_tool"):
                result = call_mcp_tool(plan["tool_name"], **plan.get("args", {}))
                # 可选：再让模型生成最终回答
                final_resp = llm.invoke(f"User asked: {query}\nTool result: {result}\nPlease answer concisely.")
                return final_resp.content
    except:
        pass

    return text  # 模型直接回答

# --- 4. 测试 ---
if __name__ == "__main__":
    question = "今天几点了？另外查一下 DeepSeek 最新发布的模型是什么？"
    print("Question:", question)
    answer = run_agent(question)
    print("Answer:", answer)