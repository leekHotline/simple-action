from fastmcp import FastMCP
from datetime import datetime
from external_tool import web_search_api # 复用函数


mcp = FastMCP("My Mcp Server")

@mcp.tool
def get_current_time() -> str:
    """
    函数作用:获取当前时间
    入参:无
    回参:字符串类型的标准化当前时间
    """
    return datetime.now().strftime('%Y-%m-%d %Y:%M:%S')

@mcp.tool
def web_search(query: str) -> str:
    """
    函数作用:根据关键词进行网络搜索
    入参:字符串类型的关键词
    回参:字符串类型的搜索结果
    """
    return web_search_api(query)

if __name__ == "__main__":
    mcp.run()