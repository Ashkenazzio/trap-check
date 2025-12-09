import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# Validation
def validate_config():
    """Validate required configuration. SerpAPI is optional (uses mock data if missing)."""
    if not ANTHROPIC_API_KEY:
        raise ValueError("Missing ANTHROPIC_API_KEY - required for Claude analysis")

    if not SERPAPI_KEY:
        print("Note: SERPAPI_KEY not set - using mock data for development")
