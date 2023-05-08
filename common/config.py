import os
from dotenv import load_dotenv, find_dotenv


class Config:
    def __init__(self):
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
        self.DATA_UPLOAD_PATH = os.getenv("DATA_UPLOAD_PATH")
        self.CHROMA_HOST = os.getenv("CHROMA_HOST")
        self.CHROMA_PORT = os.getenv("CHROMA_PORT")
        self.APP_KEY = os.getenv("APP_KEY")

