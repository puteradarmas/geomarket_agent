import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GMAPS_API_KEY = os.environ.get("GMAPS_API_KEY")
ROUTES_API_KEY = os.environ.get("ROUTES_API_KEY")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL")
LLM_NAME = os.environ.get("LLM_NAME")
VLM_BASE_URL = os.environ.get("VLM_BASE_URL")
VLM_NAME = os.environ.get("VLM_NAME")