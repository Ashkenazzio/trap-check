import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Validation
def validate_config():
    """Validate required configuration. SerpAPI is optional (uses mock data if missing)."""
    if not GOOGLE_API_KEY:
        raise ValueError("Missing GOOGLE_API_KEY - required for Gemini analysis")

    if not SERPAPI_KEY:
        print("Note: SERPAPI_KEY not set - using mock data for development")
