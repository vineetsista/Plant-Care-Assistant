# src/services/config.py
from dotenv import load_dotenv
import os

load_dotenv()  # loads variables from .env if present

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise EnvironmentError("Set your OPENAI_API_KEY in environment or .env file")
