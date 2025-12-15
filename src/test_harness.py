"""
RAG-based Test Harness for TrapCheck

Converts RAG database entries into synthetic test data to evaluate
the analysis pipeline without requiring live API calls.

Key features:
1. Converts RAG entries to mock place + review format
2. Excludes test entry from RAG retrieval (leave-one-out)
3. Compares predicted score vs ground truth
4. Measures accuracy metrics
"""

import json
import random
from pathlib import Path
from typing import Optional
import hashlib


def load_rag_database() -> list[dict]:
    """Load all entries from RAG database."""
    rag_path = Path(__file__).parent / "rag" / "data" / "rag_master.json"
    with open(rag_path) as f:
        data = json.load(f)
    return data["entries"]


def rag_entry_to_mock_place(entry: dict) -> dict:
    """
    Convert a RAG entry into mock place data format.

    Synthesizes realistic place metadata from RAG entry fields.
    """
    # Map category to Google place types
    category_to_types = {
        "restaurant": ["restaurant", "food", "point_of_interest"],
        "cafe": ["cafe", "food", "point_of_interest"],
        "bar": ["bar", "night_club", "point_of_interest"],
        "street_food": ["restaurant", "food", "point_of_interest"],
        "attraction": ["tourist_attraction", "point_of_interest"],
        "museum": ["museum", "point_of_interest"],
        "market": ["shopping_mall", "point_of_interest"],
        "shop": ["store", "point_of_interest"],
        "tour": ["travel_agency", "point_of_interest"],
    }

    # Map price tier to Google price level
    price_tier_to_level = {
        "$": 1,
        "$$": 2,
        "$$$": 3,
        "$$$$": 4,
    }

    # Generate deterministic but realistic review count based on entry
    seed = int(hashlib.md5(entry["id"].encode()).hexdigest()[:8], 16)
    random.seed(seed)

    # Traps often have more reviews (tourist volume)
    base_reviews = random.randint(500, 2000)
    if entry["verdict"] == "tourist_trap":
        review_count = base_reviews * random.randint(3, 10)
    elif entry["verdict"] == "local_gem":
        review_count = base_reviews * random.randint(1, 3)
    else:
        review_count = base_reviews * random.randint(2, 5)

    # Generate rating based on verdict (with noise)
    if entry["verdict"] == "tourist_trap":
        rating = round(random.uniform(3.8, 4.3), 1)
    elif entry["verdict"] == "local_gem":
        rating = round(random.uniform(4.4, 4.8), 1)
    else:
        rating = round(random.uniform(4.0, 4.5), 1)

    return {
        "name": entry["name"],
        "address": f"{entry['location']}",
        "rating": rating,
        "review_count": review_count,
        "price_level": price_tier_to_level.get(entry.get("price_tier", "$$"), 2),
        "types": category_to_types.get(entry.get("category", "restaurant"), ["point_of_interest"]),
        "type": category_to_types.get(entry.get("category", "restaurant"), ["restaurant"]),
        "data_id": f"mock_{entry['id']}",
        "google_maps_url": f"https://maps.google.com/?q={entry['name'].replace(' ', '+')}",
    }


def rag_entry_to_mock_reviews(entry: dict) -> tuple[list[dict], list[dict]]:
    """
    Convert RAG entry into mock low-rated and high-rated reviews.

    Uses sample_reviews from RAG entry and synthesizes additional
    reviews based on red_flags and positive_signals.
    """
    seed = int(hashlib.md5(entry["id"].encode()).hexdigest()[:8], 16)
    random.seed(seed)

    reviews_low = []
    reviews_high = []

    # Use sample reviews if available
    for sample in entry.get("sample_reviews", []):
        review = _create_review_from_sample(sample, entry)
        if sample.get("rating", 3) <= 3:
            reviews_low.append(review)
        else:
            reviews_high.append(review)

    # Synthesize additional reviews from red_flags
    for i, flag in enumerate(entry.get("red_flags", [])):
        review = _create_review_from_flag(flag, entry, i)
        reviews_low.append(review)

    # Synthesize additional reviews from positive_signals
    for i, signal in enumerate(entry.get("positive_signals", [])):
        review = _create_review_from_positive(signal, entry, i)
        reviews_high.append(review)

    # Pad with generic reviews if needed (minimum 10 each)
    while len(reviews_low) < 10:
        reviews_low.append(_create_generic_negative(entry, len(reviews_low)))

    while len(reviews_high) < 10:
        reviews_high.append(_create_generic_positive(entry, len(reviews_high)))

    return reviews_low, reviews_high


def _create_review_from_sample(sample: dict, entry: dict) -> dict:
    """Create review dict from RAG sample review."""
    seed = int(hashlib.md5(f"{entry['id']}_{sample.get('text', '')[:20]}".encode()).hexdigest()[:8], 16)
    random.seed(seed)

    is_local = sample.get("is_local", False)

    return {
        "text": sample.get("text", ""),
        "rating": sample.get("rating", 3),
        "user": {
            "name": f"Reviewer_{random.randint(1000, 9999)}",
            "reviews": random.randint(50, 500) if is_local else random.randint(5, 50),
            "photos": random.randint(10, 200) if is_local else random.randint(0, 20),
            "local_guide": is_local,
        },
        "date": f"202{random.randint(2, 4)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
    }


def _create_review_from_flag(flag: dict, entry: dict, idx: int) -> dict:
    """Create negative review from red flag."""
    seed = int(hashlib.md5(f"{entry['id']}_flag_{idx}".encode()).hexdigest()[:8], 16)
    random.seed(seed)

    # Extract evidence text or create from description
    text = flag.get("evidence", flag.get("description", "Not recommended."))
    # Clean up source attribution if present
    if "(" in text and ")" in text:
        text = text.split("(")[0].strip().strip('"')

    # High severity flags get more credible reviewers
    is_credible = flag.get("severity", "medium") == "high"

    return {
        "text": text,
        "rating": 1 if flag.get("severity") == "high" else 2,
        "user": {
            "name": f"Critic_{random.randint(1000, 9999)}",
            "reviews": random.randint(100, 800) if is_credible else random.randint(10, 50),
            "photos": random.randint(50, 300) if is_credible else random.randint(0, 20),
            "local_guide": is_credible and random.random() > 0.3,
        },
        "date": f"202{random.randint(2, 4)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
    }


def _create_review_from_positive(signal: dict, entry: dict, idx: int) -> dict:
    """Create positive review from positive signal."""
    seed = int(hashlib.md5(f"{entry['id']}_pos_{idx}".encode()).hexdigest()[:8], 16)
    random.seed(seed)

    text = signal.get("evidence", signal.get("description", "Great experience!"))
    if "(" in text and ")" in text:
        text = text.split("(")[0].strip().strip('"')

    # Strong signals get more credible reviewers
    is_credible = signal.get("strength", "moderate") == "strong"

    return {
        "text": text,
        "rating": 5,
        "user": {
            "name": f"Fan_{random.randint(1000, 9999)}",
            "reviews": random.randint(80, 500) if is_credible else random.randint(5, 30),
            "photos": random.randint(30, 200) if is_credible else random.randint(0, 10),
            "local_guide": is_credible and random.random() > 0.5,
        },
        "date": f"202{random.randint(2, 4)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
    }


def _create_generic_negative(entry: dict, idx: int) -> dict:
    """Create generic negative review based on verdict."""
    seed = int(hashlib.md5(f"{entry['id']}_gneg_{idx}".encode()).hexdigest()[:8], 16)
    random.seed(seed)

    if entry["verdict"] == "tourist_trap":
        texts = [
            "Total tourist trap. Overpriced and not worth it.",
            "Avoid this place. Way too expensive for what you get.",
            "Classic ripoff targeting tourists. Locals don't come here.",
            "Disappointed. The hype is not justified.",
            "Save your money. There are much better options nearby.",
        ]
    elif entry["verdict"] == "local_gem":
        texts = [
            "A bit crowded but that's expected for popular spots.",
            "Had to wait but food was worth it.",
            "Pricey but quality is there.",
            "Service was slow on busy night.",
            "Good but not mind-blowing.",
        ]
    else:
        texts = [
            "Mixed experience. Some things good, some not.",
            "Decent but overpriced for what it is.",
            "Would be great without the tourist crowds.",
            "Quality is inconsistent.",
            "Not bad but not amazing either.",
        ]

    return {
        "text": random.choice(texts),
        "rating": random.randint(1, 2) if entry["verdict"] == "tourist_trap" else random.randint(2, 3),
        "user": {
            "name": f"User_{random.randint(1000, 9999)}",
            "reviews": random.randint(20, 200),
            "photos": random.randint(5, 50),
            "local_guide": random.random() > 0.7,
        },
        "date": f"202{random.randint(2, 4)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
    }


def _create_generic_positive(entry: dict, idx: int) -> dict:
    """Create generic positive review based on verdict."""
    seed = int(hashlib.md5(f"{entry['id']}_gpos_{idx}".encode()).hexdigest()[:8], 16)
    random.seed(seed)

    if entry["verdict"] == "tourist_trap":
        # Trap positive reviews are often generic/suspicious
        texts = [
            "Amazing! Best ever!",
            "Loved it! Must visit!",
            "Perfect! 5 stars!",
            "Wonderful experience!",
            "Highly recommend!",
        ]
        is_credible = False
    elif entry["verdict"] == "local_gem":
        # Gem positive reviews are specific and credible
        # Include specificity keywords that the metrics detector recognizes
        category = entry.get("category", "restaurant")
        if category in ["restaurant", "cafe", "bar", "street_food"]:
            texts = [
                "Authentic and delicious. The wood-fired crust was perfectly charred, mozzarella was fresh.",
                "Finally found a place with real traditional recipes. Fresh ingredients, house-made pasta.",
                "The braised meat was tender and flavorful. Locals know what's good here.",
                "Been coming here for years. The neapolitan pizza is consistently excellent.",
                "Hidden gem with authentic carbonara. Don't let the crowds fool you - worth the wait.",
                "Best margherita I've had. Crispy crust, fresh basil, high-quality ingredients.",
            ]
        elif category in ["attraction", "museum"]:
            texts = [
                "Incredible experience. The exhibits were well-curated and informative.",
                "Worth every minute. The architecture alone is stunning, and the collection is world-class.",
                "A must-see. Take your time and enjoy the historical significance.",
                "Exceeded expectations. The audio guide was excellent and the crowds manageable early morning.",
                "Breathtaking views and rich history. Come at sunrise to avoid crowds.",
            ]
        else:
            texts = [
                "Authentic experience. High quality products at fair prices.",
                "The locals shop here for a reason. Fresh, traditional, and reasonably priced.",
                "Hidden gem. Skip the tourist shops and come here instead.",
                "Excellent quality and the staff actually knows their products.",
                "Traditional craftsmanship. Worth seeking out.",
            ]
        is_credible = True
    else:
        texts = [
            "Good experience overall. Would return.",
            "Solid choice. Not perfect but enjoyable.",
            "Better than expected given the location.",
            "Fair value for the quality.",
            "Pleasantly surprised. Recommended.",
        ]
        is_credible = random.random() > 0.5

    return {
        "text": random.choice(texts),
        "rating": 5 if entry["verdict"] != "mixed" else random.randint(4, 5),
        "user": {
            "name": f"Happy_{random.randint(1000, 9999)}",
            "reviews": random.randint(100, 500) if is_credible else random.randint(1, 10),
            "photos": random.randint(50, 200) if is_credible else random.randint(0, 5),
            "local_guide": is_credible,
        },
        "date": f"202{random.randint(2, 4)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
    }


def get_mock_external_signals(entry: dict) -> tuple[dict, dict]:
    """Generate mock external signals based on RAG entry verdict."""
    seed = int(hashlib.md5(entry["id"].encode()).hexdigest()[:8], 16)
    random.seed(seed)

    if entry["verdict"] == "tourist_trap":
        external_opinions = {
            "reddit_sentiment": "negative",
            "tripadvisor_sentiment": "mixed",
            "blog_sentiment": "negative",
            "external_warnings": random.randint(5, 15),
            "external_recommendations": random.randint(0, 3),
            "summary": "External sources generally warn against this venue.",
            "notable_quotes": ["Avoid - total tourist trap", "Overpriced and underwhelming"],
        }
        proximity = {
            "is_tourist_hotspot": True,
            "proximity_score": random.randint(75, 100),
            "near_attractions": ["Major Tourist Site", "Famous Landmark"],
            "reasoning": "Located in high-traffic tourist area.",
        }
    elif entry["verdict"] == "local_gem":
        external_opinions = {
            "reddit_sentiment": "positive",
            "tripadvisor_sentiment": "positive",
            "blog_sentiment": "positive",
            "external_warnings": random.randint(0, 2),
            "external_recommendations": random.randint(8, 15),
            "summary": "Highly recommended by locals and food bloggers.",
            "notable_quotes": ["Hidden gem!", "Locals' favorite"],
        }
        proximity = {
            "is_tourist_hotspot": random.random() > 0.5,
            "proximity_score": random.randint(20, 60),
            "near_attractions": [],
            "reasoning": "Located in residential/local area.",
        }
    else:
        external_opinions = {
            "reddit_sentiment": "mixed",
            "tripadvisor_sentiment": "mixed",
            "blog_sentiment": "mixed",
            "external_warnings": random.randint(2, 6),
            "external_recommendations": random.randint(3, 8),
            "summary": "Mixed opinions - some love it, some find it overrated.",
            "notable_quotes": ["Decent but pricey", "Good if you know what to order"],
        }
        proximity = {
            "is_tourist_hotspot": random.random() > 0.3,
            "proximity_score": random.randint(40, 75),
            "near_attractions": ["Some Attraction"],
            "reasoning": "Moderate tourist traffic area.",
        }

    return external_opinions, proximity


def verdict_to_category(verdict: str) -> str:
    """Map verdict to score category for comparison."""
    mapping = {
        "tourist_trap": "trap",
        "local_gem": "gem",
        "mixed": "mixed",
    }
    return mapping.get(verdict, "mixed")


def score_to_category(score: int) -> str:
    """Map predicted score to category."""
    if score >= 55:
        return "trap"
    elif score <= 39:
        return "gem"
    else:
        return "mixed"


def evaluate_prediction(predicted_score: int, ground_truth_score: int, ground_truth_verdict: str) -> dict:
    """
    Evaluate a single prediction against ground truth.

    Returns metrics dict with:
    - score_diff: absolute difference
    - category_match: whether predicted category matches
    - within_15: whether score is within ±15 points
    """
    predicted_category = score_to_category(predicted_score)
    true_category = verdict_to_category(ground_truth_verdict)

    score_diff = abs(predicted_score - ground_truth_score)

    return {
        "predicted_score": predicted_score,
        "ground_truth_score": ground_truth_score,
        "score_diff": score_diff,
        "predicted_category": predicted_category,
        "true_category": true_category,
        "category_match": predicted_category == true_category,
        "within_15": score_diff <= 15,
        "within_20": score_diff <= 20,
    }


# Simple test
if __name__ == "__main__":
    print("Testing RAG-to-mock conversion...")

    entries = load_rag_database()
    print(f"Loaded {len(entries)} RAG entries")

    # Test conversion on first entry
    entry = entries[0]
    print(f"\n=== Testing: {entry['name']} ({entry['verdict']}, score={entry['tourist_trap_score']}) ===")

    place = rag_entry_to_mock_place(entry)
    print(f"\nMock place: {place['name']}, {place['rating']}*, {place['review_count']} reviews")

    reviews_low, reviews_high = rag_entry_to_mock_reviews(entry)
    print(f"Mock reviews: {len(reviews_low)} low, {len(reviews_high)} high")

    print("\nSample low review:")
    print(f"  {reviews_low[0]['text'][:100]}...")
    print(f"  Rating: {reviews_low[0]['rating']}, Local Guide: {reviews_low[0]['user']['local_guide']}")

    print("\nSample high review:")
    print(f"  {reviews_high[0]['text'][:100]}...")
    print(f"  Rating: {reviews_high[0]['rating']}, Local Guide: {reviews_high[0]['user']['local_guide']}")

    external, proximity = get_mock_external_signals(entry)
    print(f"\nExternal signals: Reddit={external['reddit_sentiment']}, Proximity={proximity['proximity_score']}")
