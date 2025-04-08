import os

from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file into environment

DATABASE_URL = os.getenv("DATABASE_URL", "")
WEB_URL = os.getenv("WEB_URL", "*")
ENV = os.getenv("ENV", "development")
