import httpx
from loguru import logger

def get_city_weather(city_name) -> str :
    # 第一步：用 Nominatim 获取城市经纬度（Open-Meteo 需要经纬度）
    geo_url = f"https://nominatim.openstreetmap.org/search?city={city_name}&format=json&limit=1"
    geo_resp = httpx.get(geo_url, headers={"User-Agent": "weather_app"})
    if not geo_resp.json():
        return "城市未找到"
    loc = geo_resp.json()[0]
    lat, lon = loc["lat"], loc["lon"]

    # 第二步：调用 Open-Meteo 获取当前天气
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    weather_resp = httpx.get(weather_url)
    data = weather_resp.json()
    current = data["current_weather"]
    return f"{city_name} 当前温度: {current['temperature']}°C, 天气代码: {current['weathercode']}"

logger.info(get_city_weather('ShenZhen'))

# TODO 由于古巴哈瓦那位置限制 handshark握手失败
# import asyncio
# from aiohttp import ClientSession

# async def weather_main(city: str):
#     async with ClientSession() as session:
#         async with session.get(f'https://wttr.in/{city}?format=3') as resp:
#             data = await resp.text() # 返回的是纯文本 不是json
#             logger.info(f"http response is: {data.strip()}")
            

# asyncio.run(weather_main('Beijing'))