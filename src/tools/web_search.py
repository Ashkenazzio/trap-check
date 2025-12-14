"""
Web search module using Gemini with Google Search grounding.
Provides external opinion search and tourist proximity checks without using SerpAPI.
"""
import json
import httpx
from src.config import GOOGLE_API_KEY

# Gemini API with grounding
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"


def search_external_opinions(venue_name: str, location: str, venue_type: str = "general") -> dict:
    """
    Search Reddit, TripAdvisor forums, and relevant blogs for external opinions.
    Uses Gemini 2.0 Flash with Google Search grounding.

    Args:
        venue_name: Name of the venue (e.g., "Pizzeria Da Michele")
        location: City/region (e.g., "Naples, Italy")
        venue_type: Type of venue (restaurant, museum, attraction, tour, shop, general)

    Returns:
        {
            "external_warnings": int,       # Count of "avoid/trap" mentions
            "external_recommendations": int, # Count of positive mentions
            "reddit_sentiment": str,         # "negative", "mixed", "positive", "none"
            "tripadvisor_sentiment": str,
            "blog_sentiment": str,
            "notable_quotes": [str],         # Key excerpts
            "summary": str                   # LLM-generated summary
        }
    """
    if not GOOGLE_API_KEY:
        return {
            "error": "GOOGLE_API_KEY not configured",
            "external_warnings": 0,
            "external_recommendations": 0,
            "reddit_sentiment": "none",
            "tripadvisor_sentiment": "none",
            "blog_sentiment": "none",
            "notable_quotes": [],
            "summary": "Web search unavailable - no API key"
        }

    # Venue-type specific sources and subreddits
    source_config = {
        "restaurant": {
            "subreddits": "r/travel, r/foodie, r/food, city-specific subreddits",
            "blogs": "Food blogger opinions and restaurant review articles",
        },
        "museum": {
            "subreddits": "r/travel, r/museums, r/ArtHistory, city-specific subreddits",
            "blogs": "Travel blogger opinions, museum review articles, and art blogs",
        },
        "attraction": {
            "subreddits": "r/travel, r/solotravel, city-specific subreddits",
            "blogs": "Travel blogger opinions and destination review articles",
        },
        "tour": {
            "subreddits": "r/travel, r/solotravel, city-specific subreddits",
            "blogs": "Travel blogger opinions and tour review articles",
        },
        "shop": {
            "subreddits": "r/travel, r/shopping, city-specific subreddits",
            "blogs": "Travel blogger opinions and shopping guide articles",
        },
        "general": {
            "subreddits": "r/travel, city-specific subreddits",
            "blogs": "Travel blogger opinions and review articles",
        },
    }

    config = source_config.get(venue_type, source_config["general"])

    prompt = f"""Search for opinions about "{venue_name}" in {location} from Reddit, TripAdvisor forums, and relevant blogs.

Focus on finding:
1. Reddit discussions ({config['subreddits']})
2. TripAdvisor forum posts (not just reviews, but forum discussions)
3. {config['blogs']}

For each source, determine:
- Is the sentiment positive, negative, mixed, or no mentions found?
- Are there warnings about it being a tourist trap or overpriced?
- Are there recommendations from locals or experienced travelers?

Return your analysis as JSON with this exact structure:
{{
    "external_warnings": <number of distinct warnings/negative mentions>,
    "external_recommendations": <number of distinct positive recommendations>,
    "reddit_sentiment": "<positive|negative|mixed|none>",
    "tripadvisor_sentiment": "<positive|negative|mixed|none>",
    "blog_sentiment": "<positive|negative|mixed|none>",
    "notable_quotes": ["<quote 1>", "<quote 2>", ...],
    "summary": "<2-3 sentence summary of external opinions>"
}}

Be accurate - if you can't find mentions on a platform, use "none" for sentiment.
Only include actual quotes you found, not fabricated ones."""

    try:
        response = httpx.post(
            GEMINI_API_URL,
            params={"key": GOOGLE_API_KEY},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "tools": [{"google_search": {}}],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 2048,
                }
            },
            timeout=30.0
        )
        response.raise_for_status()
        result = response.json()

        # Extract response text
        response_text = result["candidates"][0]["content"]["parts"][0]["text"]

        # Try to parse as JSON
        # Find JSON in response (might have markdown code blocks)
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)

        # Fallback if JSON parsing fails
        return {
            "external_warnings": 0,
            "external_recommendations": 0,
            "reddit_sentiment": "none",
            "tripadvisor_sentiment": "none",
            "blog_sentiment": "none",
            "notable_quotes": [],
            "summary": response_text[:500],
            "parse_error": True
        }

    except httpx.HTTPStatusError as e:
        return {
            "error": f"HTTP error: {e.response.status_code}",
            "external_warnings": 0,
            "external_recommendations": 0,
            "reddit_sentiment": "none",
            "tripadvisor_sentiment": "none",
            "blog_sentiment": "none",
            "notable_quotes": [],
            "summary": "Web search failed"
        }
    except Exception as e:
        return {
            "error": str(e),
            "external_warnings": 0,
            "external_recommendations": 0,
            "reddit_sentiment": "none",
            "tripadvisor_sentiment": "none",
            "blog_sentiment": "none",
            "notable_quotes": [],
            "summary": "Web search failed"
        }


def check_tourist_proximity(venue_name: str, address: str, location: str) -> dict:
    """
    Check if venue is in a major tourist area.
    Uses Gemini with Google Search grounding to identify nearby attractions.

    Args:
        venue_name: Name of the venue
        address: Street address of the venue
        location: City/region

    Returns:
        {
            "near_attractions": ["attraction1", "attraction2"],
            "is_tourist_hotspot": bool,
            "proximity_score": 0-100 (100 = very touristy area),
            "reasoning": str
        }
    """
    if not GOOGLE_API_KEY:
        return {
            "error": "GOOGLE_API_KEY not configured",
            "near_attractions": [],
            "is_tourist_hotspot": False,
            "proximity_score": 50,
            "reasoning": "Unable to determine - no API key"
        }

    prompt = f"""Analyze the location of "{venue_name}" at {address}, {location}.

1. What major tourist attractions are within 500 meters of this address?
2. Is this area known as a heavily touristed zone?
3. Do tourists frequently pass by this location?

Return your analysis as JSON with this exact structure:
{{
    "near_attractions": ["<attraction 1>", "<attraction 2>", ...],
    "is_tourist_hotspot": <true|false>,
    "proximity_score": <0-100, where 100 = extremely touristy like Times Square or Trevi Fountain area>,
    "reasoning": "<1-2 sentence explanation>"
}}

Be specific about actual nearby landmarks. A proximity_score of:
- 0-30: Residential or local neighborhood
- 31-60: Some tourist activity but not a hotspot
- 61-80: Popular tourist area
- 81-100: Major tourist destination (e.g., within sight of famous landmarks)"""

    try:
        response = httpx.post(
            GEMINI_API_URL,
            params={"key": GOOGLE_API_KEY},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "tools": [{"google_search": {}}],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 1024,
                }
            },
            timeout=30.0
        )
        response.raise_for_status()
        result = response.json()

        # Extract response text
        response_text = result["candidates"][0]["content"]["parts"][0]["text"]

        # Try to parse as JSON
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            return json.loads(json_str)

        # Fallback
        return {
            "near_attractions": [],
            "is_tourist_hotspot": False,
            "proximity_score": 50,
            "reasoning": response_text[:300],
            "parse_error": True
        }

    except httpx.HTTPStatusError as e:
        return {
            "error": f"HTTP error: {e.response.status_code}",
            "near_attractions": [],
            "is_tourist_hotspot": False,
            "proximity_score": 50,
            "reasoning": "Unable to determine location characteristics"
        }
    except Exception as e:
        return {
            "error": str(e),
            "near_attractions": [],
            "is_tourist_hotspot": False,
            "proximity_score": 50,
            "reasoning": "Unable to determine location characteristics"
        }


# Mock data for testing without API calls
MOCK_WEB_SEARCH = {
    "da_michele": {
        "external_warnings": 1,
        "external_recommendations": 8,
        "reddit_sentiment": "positive",
        "tripadvisor_sentiment": "positive",
        "blog_sentiment": "positive",
        "notable_quotes": [
            "r/Naples: 'Da Michele is the real deal, just be prepared to wait'",
            "r/italy: 'Worth the hype, authentic Neapolitan pizza'",
            "Serious Eats: 'The margherita here sets the standard'"
        ],
        "summary": "Overwhelmingly positive reception across Reddit and food blogs. Consistently recommended as authentic despite crowds. Minor complaints about wait times but food quality praised."
    },
    "olive_garden_times_square": {
        "external_warnings": 12,
        "external_recommendations": 0,
        "reddit_sentiment": "negative",
        "tripadvisor_sentiment": "negative",
        "blog_sentiment": "negative",
        "notable_quotes": [
            "r/NYC: 'The fact that Olive Garden in Times Square exists is a crime against Italian food'",
            "r/travel: 'Please don't eat at chain restaurants in NYC, you're surrounded by amazing food'",
            "Eater NY: 'The Times Square Olive Garden is a monument to tourist confusion'"
        ],
        "summary": "Universally mocked on Reddit and food blogs as the quintessential tourist trap. No recommendations from locals or food writers. Frequently cited as an example of what NOT to do in NYC."
    },
    "katzs_deli": {
        "external_warnings": 2,
        "external_recommendations": 7,
        "reddit_sentiment": "positive",
        "tripadvisor_sentiment": "mixed",
        "blog_sentiment": "positive",
        "notable_quotes": [
            "r/NYC: 'Yes it's expensive, yes it's touristy, but the pastrami is genuinely the best'",
            "r/food: 'Katz's is a NY institution - worth going once'",
            "NY Times: 'The pastrami sandwich remains one of the city's great pleasures'"
        ],
        "summary": "Recognized as a legitimate NYC institution despite high prices and tourist crowds. Reddit users acknowledge it's expensive but recommend it for the quality. Some warn about prices but not the food."
    },
    "carlo_menta": {
        "external_warnings": 4,
        "external_recommendations": 3,
        "reddit_sentiment": "mixed",
        "tripadvisor_sentiment": "mixed",
        "blog_sentiment": "mixed",
        "notable_quotes": [
            "r/rome: 'Carlo Menta is fine for what it is - cheap tourist food in Trastevere'",
            "r/travel: 'It's not a scam, just volume dining. You get what you pay for'",
            "The Roman Guy blog: 'Classic example of a high-volume Trastevere tourist spot'"
        ],
        "summary": "Divisive opinions - budget travelers appreciate the low prices while food purists criticize quality. Not universally condemned as a trap, but clearly operates on volume model targeting tourists. Locals avoid it."
    },
}

MOCK_PROXIMITY = {
    "da_michele": {
        "near_attractions": ["Naples Cathedral", "Spaccanapoli", "Via dei Tribunali"],
        "is_tourist_hotspot": False,
        "proximity_score": 45,
        "reasoning": "Located in the historic center but in a more local neighborhood. The area has tourists but isn't a major attraction zone."
    },
    "olive_garden_times_square": {
        "near_attractions": ["Times Square", "Broadway Theaters", "TKTS Booth", "Madame Tussauds"],
        "is_tourist_hotspot": True,
        "proximity_score": 98,
        "reasoning": "Located directly in Times Square, one of the most heavily touristed areas in the world. Maximum tourist density."
    },
    "katzs_deli": {
        "near_attractions": ["Lower East Side Tenement Museum", "New Museum"],
        "is_tourist_hotspot": False,
        "proximity_score": 40,
        "reasoning": "Located in the Lower East Side, a neighborhood with some tourist interest but primarily residential and local businesses."
    },
    "carlo_menta": {
        "near_attractions": ["Piazza Santa Maria in Trastevere", "Basilica di Santa Maria", "Tiber River"],
        "is_tourist_hotspot": True,
        "proximity_score": 75,
        "reasoning": "Located in Trastevere, a popular tourist neighborhood in Rome. High foot traffic from tourists exploring the area."
    },
}


def get_mock_web_search(venue_key: str) -> dict:
    """Get mock web search results for testing."""
    return MOCK_WEB_SEARCH.get(venue_key, {
        "external_warnings": 0,
        "external_recommendations": 0,
        "reddit_sentiment": "none",
        "tripadvisor_sentiment": "none",
        "blog_sentiment": "none",
        "notable_quotes": [],
        "summary": "No mock data available for this venue"
    })


def get_mock_proximity(venue_key: str) -> dict:
    """Get mock proximity data for testing."""
    return MOCK_PROXIMITY.get(venue_key, {
        "near_attractions": [],
        "is_tourist_hotspot": False,
        "proximity_score": 50,
        "reasoning": "No mock data available for this venue"
    })
