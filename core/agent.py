import os
from loguru import logger
import httpx
import langchain_core
import fastmcp

from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('DEEPSEEK_API_KEY')
logger.info(API_KEY)

