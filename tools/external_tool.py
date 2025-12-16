# 外部api工具函数 和 可复用mcp服务
import os
from exa_py import Exa
from dotenv import load_dotenv

load_dotenv()
exa_api_key = os.getenv('EXA_API_KEY')

def web_search_api(keyword: str) -> str:
    "调用网络搜索api 得到结果"
    exa = Exa(exa_api_key)
    result = exa.search_and_contents(
        query= keyword,
        type= 'auto',
        text = True
    )
    return result


