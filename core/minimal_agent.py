import os
import re
import ollama
from ollama import Client
from loguru import logger

os.environ['NO_PROXY'] = '127.0.1,localhost'
# 定义工具
def get_weather(city : str) -> str:
    weather_db = {
        "BeiJing": "16°C,有雾霾",
        "ShangHai": "21°C, 天气晴朗",
        "ShenZhen": "28°C, 风大，空气潮湿",
        "GuangZhou": "30°C， 炎热，注意防嗮",
        "HangZhou": '24°C， 适合出门',
        "SuZhou" : '26°C，烟雨'
    }
    return weather_db.get(city)

def caculator(expression: str) -> str:
    try:
        return f"表达式结果为:{eval(expression)}"
    except Exception as e:
        logger.info(f"报错信息为:{str(e)}")

def web_search(query: str) -> str:
    try:
        return f"关于{query}的搜索结果，这是详细信息..."
    except Exception as e:
        logger.info(f"报错信息为:{str(e)}")

# tools就是注册工具函数的，key是函数名value是函数对象，及其干什么的描述
TOOLS = {
    "get_weather": (get_weather, '输出城市名称字符串，得到该城市当天的天气'),
    'caculator': (caculator, '输入函数表达式字符串，得到结果，例如3*5=15'),
    'web_search': (web_search, '输入关键词字符串,得到网络搜索结果')
}

# 编写系统提示词 多行字符串""" """
REACT_PROMPT = """
你是一个严格遵守格式的 AI 助手，必须使用 ReAct 格式（Thought / Action / Action Input）进行工具调用。

## 可用工具:
{tool_desc}

## 重要规则:
- 你 **不能** 直接回答问题，必须通过调用工具获取信息。
- 你 **不能** 使用 <think>、<reason> 等 XML 标签。
- 你 **必须** 严格按以下格式输出，不要添加额外内容：

Thought: 我需要获取XX信息
Action: 工具名称
Action Input: 参数

## 用户问题: {question}

开始:
Thought:"""


# agent Re-Act 循环 思考-行动-观察 OODA循环
def run_agent(question: str, max_steps = 5) -> str:
    # 定义客户端 指定进程端口
    client = Client(host='http://127.0.0.1:12345')
    client.list()

    # 构建工具描述
    tool_desc = '\n'.join([f'-{name}:{desc}' for name, (_,desc) in TOOLS.items()])
    # 初始化对话
    prompt = REACT_PROMPT.format(tool_desc=tool_desc,question=question)
    full_response = ''
    print('=' * 60) 
    print(f'问题:{question}')
    print('=' * 60)

    for step in range(max_steps):
        logger.info(f'\n --- Step {step+1} ---')

        # 调用大语言模型
        response = client.chat(
            model='qwen3:4b',
            messages= [{'role': 'user', 'content': prompt + full_response}]
        )
        llm_output = response['message']['content']
        print(llm_output)

        full_response += llm_output

        # 检查是否有最终答案
        if "Final Answer:" in llm_output:
            final = llm_output.split("Final Answer:")[-1].strip()
            print("\n" + "=" * 60)
            print(f"✅ 最终答案: {final}")
            print("=" * 60)
            return final
        
        # 提取 Action 和 Action Input
        action_match = re.search(r"Action:\s*(\w+)", llm_output)
        input_match = re.search(r"Action Input:\s*(.+?)(?:\n|$)", llm_output)
        
        if action_match and input_match:
            tool_name = action_match.group(1).strip()
            tool_input = input_match.group(1).strip()
            
            print(f"\n🔧 调用工具: {tool_name}({tool_input})")
            
            # 执行工具
            if tool_name in TOOLS:
                tool_func = TOOLS[tool_name][0]
                result = tool_func(tool_input)
                observation = f"\nObservation: {result}\nThought:"
                full_response += observation
                print(f"📋 观察结果: {result}")
            else:
                full_response += f"\nObservation: 工具 {tool_name} 不存在\nThought:"
        else:
            # 没有action，可能直接得出答案了
            break
    
    return "达到最大步数，未能完成任务"

# 测试数据并运行
if __name__ == "__main__":
    # 测试用例
    questions = [
        "BeiJing",
        "4*6",
        "multi-agent教程"
    ]

    for q in questions:
        run_agent(q)
        print("\n" + "🔸" * 30 + "\n")



# weather_reuslt = get_weather("ShenZhen")
# cal_result = caculator("3*5")
# search_result = web_search("multi-agent教程")
# logger.info(search_result)
# logger.info(cal_result)
# logger.info(weather_reuslt)