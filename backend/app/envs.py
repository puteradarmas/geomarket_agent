import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GMAPS_API_KEY = os.environ.get("GMAPS_API_KEY")
ROUTES_API_KEY = os.environ.get("ROUTES_API_KEY")