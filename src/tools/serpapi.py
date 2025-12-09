"""
SerpAPI integration for Google Maps place search and review fetching.
Falls back to mock data when SERPAPI_KEY is not configured.
"""
from src.config import SERPAPI_KEY
from src.tools.mock_data import get_mock_place, get_mock_reviews

# Only import serpapi if we have a key
if SERPAPI_KEY:
    from serpapi import GoogleSearch

USE_MOCK = not SERPAPI_KEY


def search_place(query: str, location: str | None = None) -> dict | None:
    """
    Search for a place on Google Maps.

    Args:
        query: Business name (e.g., "Pizzeria Da Michele")
        location: City/region (e.g., "Naples, Italy")

    Returns:
        Place info dict with data_id, name, address, rating, etc.
        None if not found.
    """
    if USE_MOCK:
        print("[MOCK MODE] Using mock data - no SerpAPI key configured")
        return get_mock_place(query)

    search_query = f"{query} {location}" if location else query

    params = {
        "engine": "google_maps",
        "q": search_query,
        "type": "search",
        "api_key": SERPAPI_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    # Handle both single place result and list of results
    place = None
    if "place_results" in results:
        # Direct place match
        place = results["place_results"]
    elif "local_results" in results and results["local_results"]:
        # List of results
        place = results["local_results"][0]

    if not place:
        return None

    return {
        "data_id": place.get("data_id"),
        "place_id": place.get("place_id"),
        "name": place.get("title"),
        "address": place.get("address"),
        "rating": place.get("rating"),
        "review_count": place.get("reviews"),
        "price_level": place.get("price"),
        "type": place.get("type", [place.get("type")] if isinstance(place.get("type"), str) else place.get("type", [])),
        "types": place.get("type_ids", []),
        "gps_coordinates": place.get("gps_coordinates"),
        "google_maps_url": place.get("website") or f"https://www.google.com/maps/place/?q=place_id:{place.get('place_id')}",
        "thumbnail": place.get("thumbnail"),
        "rating_summary": place.get("rating_summary"),  # Rating distribution!
    }


def fetch_reviews(
    data_id: str,
    sort_by: str = "qualityScore",
    max_reviews: int = 50,
) -> dict:
    """
    Fetch reviews for a place using its data_id.

    Args:
        data_id: Google Maps data ID from search_place
        sort_by: 'qualityScore', 'newestFirst', 'ratingHigh', 'ratingLow'
        max_reviews: Maximum number of reviews to fetch

    Returns:
        Dict with place_info, reviews list, and topics
    """
    if USE_MOCK:
        mock_data = get_mock_reviews(data_id)
        if mock_data:
            return mock_data
        return {"place_info": {}, "reviews": [], "topics": []}

    all_reviews = []
    next_page_token = None

    # Map sort options to SerpAPI values
    sort_map = {
        "qualityScore": "qualityScore",
        "newestFirst": "newestFirst",
        "ratingHigh": "ratingHigh",
        "ratingLow": "ratingLow",
    }

    while len(all_reviews) < max_reviews:
        params = {
            "engine": "google_maps_reviews",
            "data_id": data_id,
            "sort_by": sort_map.get(sort_by, "qualityScore"),
            "api_key": SERPAPI_KEY,
        }

        if next_page_token:
            params["next_page_token"] = next_page_token

        search = GoogleSearch(params)
        results = search.get_dict()

        # Extract place info (only on first page)
        place_info = results.get("place_info", {})

        # Extract reviews
        reviews = results.get("reviews", [])
        if not reviews:
            break

        for review in reviews:
            all_reviews.append({
                "text": review.get("snippet", ""),
                "rating": review.get("rating"),
                "date": review.get("date"),
                "iso_date": review.get("iso_date"),
                "user": {
                    "name": review.get("user", {}).get("name", "Anonymous"),
                    "local_guide": review.get("user", {}).get("local_guide", False),
                    "reviews_count": review.get("user", {}).get("reviews"),
                    "photos": review.get("user", {}).get("photos"),
                },
                "likes": review.get("likes", 0),
                "images": review.get("images", []),
                "details": review.get("details", {}),
                "response": review.get("response", {}).get("snippet") if review.get("response") else None,
            })

            if len(all_reviews) >= max_reviews:
                break

        # Check for next page
        next_page_token = results.get("serpapi_pagination", {}).get("next_page_token")
        if not next_page_token:
            break

    # Extract topics/keywords
    topics = results.get("topics", [])

    return {
        "place_info": {
            "title": place_info.get("title"),
            "address": place_info.get("address"),
            "rating": place_info.get("rating"),
            "total_reviews": place_info.get("reviews"),
        },
        "reviews": all_reviews,
        "topics": [{"keyword": t.get("keyword"), "mentions": t.get("count")} for t in topics],
    }


def fetch_stratified_reviews(
    data_id: str,
    reviews_per_tier: int = 30,
) -> dict:
    """
    Fetch reviews stratified by rating for comprehensive analysis.
    Gets both lowest-rated and highest-rated reviews to detect patterns.

    Args:
        data_id: Google Maps data ID from search_place
        reviews_per_tier: Number of reviews to fetch per tier (low/high)

    Returns:
        Dict with reviews_low, reviews_high, and place_info
    """
    if USE_MOCK:
        mock_data = get_mock_reviews(data_id)
        if mock_data:
            reviews = mock_data.get("reviews", [])
            # Simulate stratification with mock data
            sorted_reviews = sorted(reviews, key=lambda r: r.get("rating", 3))
            mid = len(sorted_reviews) // 2
            return {
                "place_info": mock_data.get("place_info", {}),
                "reviews_low": sorted_reviews[:mid] or sorted_reviews,
                "reviews_high": sorted_reviews[mid:] or sorted_reviews,
                "topics": mock_data.get("topics", []),
            }
        return {"place_info": {}, "reviews_low": [], "reviews_high": [], "topics": []}

    # Fetch lowest-rated reviews (where truth often lives)
    low_result = fetch_reviews(data_id, sort_by="ratingLow", max_reviews=reviews_per_tier)

    # Fetch highest-rated reviews (to analyze for fake patterns)
    high_result = fetch_reviews(data_id, sort_by="ratingHigh", max_reviews=reviews_per_tier)

    return {
        "place_info": low_result.get("place_info") or high_result.get("place_info", {}),
        "reviews_low": low_result.get("reviews", []),
        "reviews_high": high_result.get("reviews", []),
        "topics": low_result.get("topics") or high_result.get("topics", []),
    }
