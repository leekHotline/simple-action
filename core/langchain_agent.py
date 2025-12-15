import os
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json
import httpx
from exa_py import Exa
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# 工具定义 工具绑定 思考行动观察
# 让模型知道能调用什么工具  让模型输出结构化的调用指令 思考需要是否需要调用工具调用什么工具 执行工具 观察反馈结果
load_dotenv()

exa_api_key = os.getenv('EXA_API_KEY')
os.environ['NO_PROXY'] = '127.0.1,localhost'

# ============ 1. 定义工具 ============
@tool
def get_weather(city: str) -> str:
    """获取指定城市的实时天气信息"""
    weather_db = {
        "北京": "☀️ 晴天 25°C",
        "上海": "🌥️ 多云 28°C", 
        "广州": "🌧️ 小雨 30°C",
    }
    return weather_db.get(city, f"📍 {city}：晴 26°C")

@tool  
def calculator(expression: str) -> str:
    """计算数学表达式"""
    try:
        return f"结果是：{eval(expression)}"
    except Exception as e:
        return f"计算错误：{e}"

@tool
def get_time(timezone: str = "Asia/Shanghai") -> str:
    """获取当前时间"""
    from datetime import datetime
    return f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@tool
def web_search_api(keyword: str) -> str:
    "调用网络搜索api 得到结果"
    exa = Exa(exa_api_key)
    result = exa.search_and_contents(
        query= keyword,
        type= 'auto',
        text = True
    )
    return result

@tool
def crawer_html(target_url : str) :
    "输入目标网址 得到网址的html信息 解析去掉html标签获得纯文本"
    response = httpx.get(target_url)
    response.raise_for_status()
    # 确保请求成功 检查状态码
    soup = BeautifulSoup(response.text,'html.parser')
    result = soup.get_text()
    return result


# ============ 2. 创建带工具的模型 ============
llm = ChatOllama(
    model="qwen3:8b",
    temperature=0,
    base_url='http://127.0.0.1:12345'
)

tools = [get_weather, calculator, get_time, web_search_api, crawer_html]
tool_map = {t.name: t for t in tools}

# 绑定工具到模型
llm_with_tools = llm.bind_tools(tools)

# ============ 3. ReAct 循环 ============
def run_agent(query: str, max_iterations: int = 5) -> str:
    """手写 ReAct 循环"""
    messages = [HumanMessage(content=query)]
    
    for i in range(max_iterations):
        print(f"\n--- 迭代 {i+1} ---")
        
        # 调用模型
        response = llm_with_tools.invoke(messages)
        messages.append(response)
        
        # 检查是否有工具调用
        if not response.tool_calls:
            print("✅ 模型给出最终答案")
            return response.content
        
        # 执行工具调用
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"🔧 调用工具: {tool_name}({tool_args})")
            
            # 执行工具
            if tool_name in tool_map:
                result = tool_map[tool_name].invoke(tool_args)
                print(f"📋 工具结果: {result}")
            else:
                result = f"未知工具: {tool_name}"
            
            # 添加工具结果到消息
            messages.append(ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            ))
    
    return "达到最大迭代次数"

# ============ 4. 运行测试 ============
if __name__ == "__main__":
    questions = [
        "北京今天天气怎么样？",
        "帮我算一下 123 * 456 + 789",
        "现在几点了？",
        "把我查一下lanchain_core的最新版本是多少呢?",
        "https://kissfocus.vip 是什么网址?"
    ]
    
    for q in questions:
        print(f"\n{'='*60}")
        print(f"❓ 问题: {q}")
        print('='*60)
        answer = run_agent(q)
        print(f"\n✅ 最终答案: {answer}")