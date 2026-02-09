import os
from app.settings import settings

def init_langsmith():
    if settings.LANGSMITH_API_KEY:
        os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
        os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT
    if settings.LANGCHAIN_TRACING_V2:
        os.environ["LANGCHAIN_TRACING_V2"] = settings.LANGCHAIN_TRACING_V2
    if settings.LANGCHAIN_PROJECT:
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
