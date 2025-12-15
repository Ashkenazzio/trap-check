"""
Metrics computation layer for tourist trap detection.
Computes quantitative signals from raw review data BEFORE Claude analysis.
"""
import re
from collections import Counter
from datetime import datetime

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


# Venue type constants
VENUE_TYPE_RESTAURANT = "restaurant"
VENUE_TYPE_MUSEUM = "museum"
VENUE_TYPE_ATTRACTION = "attraction"
VENUE_TYPE_TOUR = "tour"
VENUE_TYPE_SHOP = "shop"
VENUE_TYPE_GENERAL = "general"


def infer_venue_type(place: dict) -> str:
    """
    Infer venue category from Google Place types and name.

    Args:
        place: Place data dict with 'types' and 'name' fields

    Returns:
        One of: restaurant, museum, attraction, tour, shop, general
    """
    types = place.get("types", [])
    if isinstance(types, str):
        types = [types]
    types_lower = [t.lower() for t in types]

    name_lower = (place.get("name") or "").lower()
    place_type = place.get("type") or ""
    if isinstance(place_type, list):
        place_type = " ".join(place_type)
    place_type = place_type.lower()

    # Restaurant/food venues
    food_types = {"restaurant", "cafe", "bar", "bakery", "food", "meal_takeaway",
                  "meal_delivery", "night_club", "coffee_shop", "ice_cream_shop"}
    if any(t in types_lower for t in food_types) or any(kw in place_type for kw in ["restaurant", "cafe", "bar", "food"]):
        return VENUE_TYPE_RESTAURANT

    # Museums and galleries
    museum_types = {"museum", "art_gallery"}
    if any(t in types_lower for t in museum_types) or "museum" in name_lower or "gallery" in name_lower:
        return VENUE_TYPE_MUSEUM

    # Tours and experiences
    if "tour" in name_lower or "experience" in name_lower or "walking" in name_lower:
        return VENUE_TYPE_TOUR

    # Shops and markets
    shop_types = {"store", "shopping_mall", "clothing_store", "jewelry_store",
                  "gift_shop", "souvenir_shop", "market", "supermarket", "shoe_store"}
    if any(t in types_lower for t in shop_types) or "shop" in name_lower or "market" in name_lower:
        return VENUE_TYPE_SHOP

    # Tourist attractions (check after more specific types)
    attraction_types = {"tourist_attraction", "point_of_interest", "landmark",
                        "amusement_park", "aquarium", "zoo", "stadium", "church",
                        "hindu_temple", "mosque", "synagogue", "place_of_worship"}
    if any(t in types_lower for t in attraction_types):
        return VENUE_TYPE_ATTRACTION

    return VENUE_TYPE_GENERAL


# Keywords that EXPLICITLY indicate tourist trap awareness (strong signal)
# These are phrases where reviewers directly call out tourist trap behavior
TRAP_AWARENESS_KEYWORDS = [
    "tourist trap", "trap for tourist", "avoid this place", "total scam",
    "ripoff", "rip-off", "rip off", "complete waste", "don't waste your",
    "stay away", "do not go", "don't go here",
]

# General negative keywords (weaker signal - common in any negative review)
GENERAL_NEGATIVE_KEYWORDS = [
    "overpriced", "not worth", "waste of money", "disappointing",
    "avoid", "skip this", "wouldn't recommend",
]

# Keywords suggesting review manipulation
MANIPULATION_KEYWORDS = [
    "fake", "bought", "paid review", "forced to review", "asked for review",
    "in exchange", "free dessert", "free drink",
]

# Quality complaint keywords (legacy - for backwards compatibility)
QUALITY_KEYWORDS = [
    "disgusting", "terrible", "awful", "worst", "horrible", "inedible",
    "sick", "food poisoning", "diarrhea", "stomach", "bland", "tasteless",
    "frozen", "microwave", "premade", "pre-made", "canned",
]

# Venue-type-specific quality complaint keywords
QUALITY_KEYWORDS_BY_TYPE = {
    VENUE_TYPE_RESTAURANT: [
        "disgusting", "terrible", "awful", "worst", "horrible", "inedible",
        "sick", "food poisoning", "diarrhea", "stomach", "bland", "tasteless",
        "frozen", "microwave", "premade", "pre-made", "canned", "undercooked",
        "cold food", "stale", "greasy", "overcooked",
    ],
    VENUE_TYPE_MUSEUM: [
        "boring", "overcrowded", "couldn't see", "too small", "not worth",
        "misleading", "fake", "replica", "disappointing collection", "empty",
        "poorly maintained", "confusing layout", "bad lighting", "overpriced tickets",
    ],
    VENUE_TYPE_ATTRACTION: [
        "waste of time", "not worth it", "overcrowded", "overrated",
        "nothing special", "skip this", "disappointing", "underwhelming",
        "too short", "poorly organized", "dirty", "run down", "unsafe",
    ],
    VENUE_TYPE_TOUR: [
        "rushed", "couldn't hear", "too large group", "disorganized",
        "guide was late", "different than advertised", "bait and switch",
        "unprofessional", "boring guide", "waste of money", "misleading",
        "no refund", "hidden fees", "cancelled",
    ],
    VENUE_TYPE_SHOP: [
        "fake", "counterfeit", "poor quality", "overpriced", "pushy",
        "aggressive sales", "same stuff everywhere", "made in china",
        "rude staff", "pressure tactics", "bait and switch", "scam",
    ],
    VENUE_TYPE_GENERAL: [
        "disappointing", "not worth", "overrated", "waste of money",
        "underwhelming", "skip this", "terrible", "awful", "horrible",
    ],
}

# Generic praise patterns (low specificity)
GENERIC_PRAISE_PATTERNS = [
    r"\bgreat\b", r"\bamazing\b", r"\bawesome\b", r"\bwonderful\b",
    r"\bdelicious\b", r"\byummy\b", r"\btasty\b", r"\bgood\b",
    r"\bloved it\b", r"\bhighly recommend\b", r"\bmust visit\b",
    r"\b10/10\b", r"\bfive stars\b", r"\b5 stars\b",
]

# Specific detail indicators (high specificity) - legacy for backwards compatibility
SPECIFICITY_INDICATORS = [
    # Cooking methods
    r"\bwood[- ]?fired\b", r"\bcharred\b", r"\bcrispy\b", r"\bcaramelized\b",
    r"\bslow[- ]?cooked\b", r"\bbraised\b", r"\bgrilled\b", r"\broasted\b",
    # Ingredients
    r"\bmozzarella\b", r"\bburrata\b", r"\bprosciutto\b", r"\bguanciale\b",
    r"\bpancetta\b", r"\bpecorino\b", r"\bparmigiano\b", r"\bsan marzano\b",
    r"\bnduja\b", r"\btruffle\b", r"\bsaffron\b",
    # Texture/quality descriptors
    r"\bal dente\b", r"\bchewy\b", r"\btender\b", r"\bflaky\b", r"\bcrust\b",
    r"\bferment\b", r"\baged\b", r"\bfresh[- ]?made\b", r"\bhouse[- ]?made\b",
    # Comparisons
    r"\bbetter than\b", r"\breminds me of\b", r"\bjust like\b", r"\bauthentic\b",
    r"\btraditional\b", r"\boriginal recipe\b",
    # Specific dish names (partial)
    r"\bmargherita\b", r"\bmarinara\b", r"\bcarbonara\b", r"\bamatriciana\b",
    r"\bcacio e pepe\b", r"\bneapolitan\b",
]

# Venue-type-specific specificity indicators
SPECIFICITY_INDICATORS_BY_TYPE = {
    VENUE_TYPE_RESTAURANT: [
        # Cooking methods
        r"\bwood[- ]?fired\b", r"\bcharred\b", r"\bcrispy\b", r"\bcaramelized\b",
        r"\bslow[- ]?cooked\b", r"\bbraised\b", r"\bgrilled\b", r"\broasted\b",
        # Ingredients
        r"\bmozzarella\b", r"\bburrata\b", r"\bprosciutto\b", r"\bguanciale\b",
        r"\bpancetta\b", r"\bpecorino\b", r"\bparmigiano\b", r"\bsan marzano\b",
        r"\bnduja\b", r"\btruffle\b", r"\bsaffron\b",
        # Texture/quality descriptors
        r"\bal dente\b", r"\bchewy\b", r"\btender\b", r"\bflaky\b", r"\bcrust\b",
        r"\bferment\b", r"\baged\b", r"\bfresh[- ]?made\b", r"\bhouse[- ]?made\b",
        # Comparisons
        r"\bbetter than\b", r"\breminds me of\b", r"\bjust like\b", r"\bauthentic\b",
        r"\btraditional\b", r"\boriginal recipe\b",
        # Specific dish names
        r"\bmargherita\b", r"\bmarinara\b", r"\bcarbonara\b", r"\bamatriciana\b",
        r"\bcacio e pepe\b", r"\bneapolitan\b",
    ],
    VENUE_TYPE_MUSEUM: [
        # Collection/artwork terms
        r"\bexhibit\b", r"\bcollection\b", r"\boriginal\b", r"\bartwork\b",
        r"\bcurator\b", r"\baudio guide\b", r"\binteractive\b", r"\brare\b",
        # Specific art terms
        r"\bmasterpiece\b", r"\bimpressionist\b", r"\brenaissance\b", r"\bcontemporary\b",
        r"\bsculpture\b", r"\bpainting\b", r"\bartifact\b", r"\binstallation\b",
        # Experience descriptors
        r"\bwell[- ]?lit\b", r"\bspacious\b", r"\bcrowded\b", r"\bquiet\b",
        r"\beducational\b", r"\bthought[- ]?provoking\b", r"\bimmersive\b",
        # Comparisons
        r"\bbetter than\b", r"\breminds me of\b", r"\bsimilar to\b",
    ],
    VENUE_TYPE_ATTRACTION: [
        # View/scenery terms
        r"\bview\b", r"\bscenery\b", r"\bpanoramic\b", r"\bsunset\b", r"\bsunrise\b",
        # Historical/architectural terms
        r"\bhistory\b", r"\barchitecture\b", r"\bhistoric\b", r"\bcentury\b",
        r"\brestored\b", r"\boriginal\b", r"\bpreserved\b",
        # Practical details
        r"\bphoto op\b", r"\bearly morning\b", r"\bqueue\b", r"\bwaiting time\b",
        r"\bticket\b", r"\bguide\b", r"\baccess\b",
        # Experience quality
        r"\bbreathtaking\b", r"\bmust[- ]?see\b", r"\biconic\b", r"\bunique\b",
    ],
    VENUE_TYPE_TOUR: [
        # Guide quality
        r"\bguide\b", r"\bknowledgeable\b", r"\benthusiastic\b", r"\bprofessional\b",
        r"\bstory\b", r"\bhistory\b", r"\binsight\b", r"\banecdote\b",
        # Group experience
        r"\bgroup size\b", r"\bsmall group\b", r"\bprivate\b", r"\bpersonal\b",
        # Access and logistics
        r"\baccess\b", r"\bskip the line\b", r"\bbehind the scenes\b", r"\bexclusive\b",
        r"\bpick[- ]?up\b", r"\bon time\b", r"\bpunctual\b",
        # Tour specifics
        r"\bwalking\b", r"\bbus\b", r"\bboat\b", r"\bbike\b", r"\bfood tour\b",
    ],
    VENUE_TYPE_SHOP: [
        # Quality/authenticity
        r"\bhandmade\b", r"\bartisan\b", r"\blocal\b", r"\bquality\b",
        r"\bauthentic\b", r"\btraditional\b", r"\bcraftsman\b", r"\bgeniune\b",
        # Materials
        r"\bleather\b", r"\bsilk\b", r"\bceramic\b", r"\bglass\b", r"\bwood\b",
        r"\bhand[- ]?painted\b", r"\bhand[- ]?crafted\b",
        # Shopping experience
        r"\bselection\b", r"\bvariety\b", r"\bunique\b", r"\bone of a kind\b",
        r"\bfair price\b", r"\breasonable\b", r"\bbargain\b",
    ],
    VENUE_TYPE_GENERAL: [
        # Generic quality indicators
        r"\bworth\b", r"\bauthentic\b", r"\btraditional\b", r"\blocal\b",
        r"\bgenuine\b", r"\bquality\b", r"\bunique\b", r"\bspecial\b",
        # Comparisons
        r"\bbetter than\b", r"\breminds me of\b", r"\bsimilar to\b",
    ],
}

# Tourist languages for non-English speaking countries
TOURIST_LANGUAGES = {"en", "zh-cn", "zh-tw", "ja", "ko"}

# English-speaking countries (where English reviews are expected)
ENGLISH_SPEAKING_COUNTRIES = {"US", "USA", "UK", "GB", "AU", "CA", "NZ", "IE"}


def compute_reviewer_credibility(user: dict) -> dict:
    """
    Compute credibility score for a single reviewer.

    Returns dict with:
        - score: 0-100 credibility score
        - flags: list of credibility indicators
    """
    score = 50  # Base score
    flags = []

    reviews_count = user.get("reviews") or user.get("reviews_count") or 0
    photos_count = user.get("photos") or 0
    is_local_guide = user.get("local_guide", False)

    # Review count scoring
    if reviews_count >= 100:
        score += 25
        flags.append("experienced_reviewer")
    elif reviews_count >= 20:
        score += 15
        flags.append("moderate_reviewer")
    elif reviews_count >= 5:
        score += 5
    elif reviews_count <= 3:
        score -= 20
        flags.append("new_account")

    # Photo count scoring
    if photos_count >= 50:
        score += 15
        flags.append("photo_contributor")
    elif photos_count >= 10:
        score += 10
    elif photos_count == 0:
        score -= 10
        flags.append("no_photos")

    # Local Guide bonus
    if is_local_guide:
        score += 20
        flags.append("local_guide")

    return {
        "score": max(0, min(100, score)),
        "flags": flags,
        "reviews_count": reviews_count,
        "photos_count": photos_count,
        "is_local_guide": is_local_guide,
    }


def detect_keywords(text: str, keywords: list[str]) -> list[str]:
    """Find which keywords appear in text (case-insensitive)."""
    if not text:
        return []
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def compute_specificity(text: str, venue_type: str = VENUE_TYPE_GENERAL) -> int:
    """
    Score 0-100 based on how specific/detailed the review is.
    Higher = more specific details, lower = generic praise.

    Args:
        text: Review text to analyze
        venue_type: Type of venue (restaurant, museum, attraction, tour, shop, general)

    Returns:
        Specificity score 0-100
    """
    if not text:
        return 0

    text_lower = text.lower()
    score = 50  # Base score

    # Penalize generic praise
    generic_count = sum(1 for pattern in GENERIC_PRAISE_PATTERNS if re.search(pattern, text_lower))
    score -= min(generic_count * 5, 25)  # Max -25 for generic

    # Reward specific details - use venue-type-specific indicators
    indicators = SPECIFICITY_INDICATORS_BY_TYPE.get(venue_type, SPECIFICITY_INDICATORS_BY_TYPE[VENUE_TYPE_GENERAL])
    specific_count = sum(1 for pattern in indicators if re.search(pattern, text_lower))
    score += min(specific_count * 8, 40)  # Max +40 for specificity

    # Reward longer reviews (more detail)
    word_count = len(text.split())
    if word_count > 100:
        score += 15
    elif word_count > 50:
        score += 10
    elif word_count > 25:
        score += 5
    elif word_count < 10:
        score -= 15  # Very short = likely generic

    # Reward comparisons and context
    if re.search(r"\bcompared to\b|\bunlike\b|\bsimilar to\b", text_lower):
        score += 10

    # Reward price mentions (shows value assessment)
    if re.search(r"\$|\bprice\b|\bworth\b|\bexpensive\b|\bcheap\b|\bvalue\b", text_lower):
        score += 5

    return max(0, min(100, score))


def analyze_language_distribution(reviews: list[dict]) -> dict:
    """
    Detect language distribution in reviews.
    High % of tourist languages (English, Chinese, Japanese) in non-English
    speaking country = potential tourist trap signal.
    """
    if not LANGDETECT_AVAILABLE:
        return {"detected": False, "error": "langdetect not installed"}

    languages = []
    for r in reviews:
        text = r.get("text") or r.get("snippet") or ""
        if len(text) > 30:  # Need enough text for reliable detection
            try:
                lang = detect(text)
                languages.append(lang)
            except LangDetectException:
                pass

    if not languages:
        return {"detected": False, "total_analyzed": 0}

    dist = Counter(languages)
    total = len(languages)

    # Calculate tourist language percentage
    tourist_count = sum(dist.get(lang, 0) for lang in TOURIST_LANGUAGES)
    tourist_pct = (tourist_count / total) * 100 if total > 0 else 0

    return {
        "detected": True,
        "total_analyzed": total,
        "distribution": dict(dist),
        "tourist_language_pct": round(tourist_pct, 1),
        "dominant_language": dist.most_common(1)[0][0] if dist else None,
        "english_pct": round((dist.get("en", 0) / total) * 100, 1) if total > 0 else 0,
    }


def analyze_review(review: dict, venue_type: str = VENUE_TYPE_GENERAL) -> dict:
    """
    Analyze a single review and extract all metrics.

    Args:
        review: Review data dict
        venue_type: Type of venue for venue-specific keyword detection

    Returns:
        Analysis dict with credibility, keywords, ratings, etc.
    """
    text = review.get("text") or review.get("snippet") or ""
    rating = review.get("rating") or 0
    user = review.get("user") or {}

    credibility = compute_reviewer_credibility(user)

    # Keyword detection - use venue-specific quality keywords
    trap_keywords = detect_keywords(text, TRAP_AWARENESS_KEYWORDS)
    manipulation_keywords = detect_keywords(text, MANIPULATION_KEYWORDS)
    quality_kws = QUALITY_KEYWORDS_BY_TYPE.get(venue_type, QUALITY_KEYWORDS_BY_TYPE[VENUE_TYPE_GENERAL])
    quality_keywords = detect_keywords(text, quality_kws)

    # Check for photos in this review
    has_images = bool(review.get("images"))

    # Sub-ratings (food, service, atmosphere) - only relevant for restaurants
    details = review.get("details") or {}
    food_rating = None
    service_rating = None
    service_food_gap = None

    if venue_type == VENUE_TYPE_RESTAURANT:
        food_rating = details.get("Food") or details.get("food")
        service_rating = details.get("Service") or details.get("service")

        # Convert to int if string
        if isinstance(food_rating, str):
            try:
                food_rating = int(food_rating)
            except ValueError:
                food_rating = None
        if isinstance(service_rating, str):
            try:
                service_rating = int(service_rating)
            except ValueError:
                service_rating = None

        # Detect service vs food disparity (good service, bad food = trap pattern)
        if food_rating is not None and service_rating is not None:
            service_food_gap = service_rating - food_rating

    return {
        "rating": rating,
        "text_length": len(text),
        "credibility": credibility,
        "trap_keywords": trap_keywords,
        "manipulation_keywords": manipulation_keywords,
        "quality_keywords": quality_keywords,
        "has_images": has_images,
        "food_rating": food_rating,
        "service_rating": service_rating,
        "service_food_gap": service_food_gap,
        "date": review.get("date") or review.get("iso_date"),
        "likes": review.get("likes") or 0,
    }


def analyze_date_clustering(reviews: list[dict]) -> dict:
    """
    Detect suspicious patterns in review dates.
    Many reviews on the same day could indicate manipulation.
    """
    dates = []
    for r in reviews:
        iso_date = r.get("iso_date")
        if iso_date:
            try:
                # Parse ISO date and extract just the date part
                dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
                dates.append(dt.date())
            except (ValueError, AttributeError):
                pass

    if not dates:
        return {"clustered_dates": [], "max_same_day": 0, "clustering_score": 0}

    date_counts = Counter(dates)
    most_common = date_counts.most_common(5)

    # Flag dates with 3+ reviews
    clustered = [(str(d), c) for d, c in most_common if c >= 3]
    max_same_day = most_common[0][1] if most_common else 0

    # Clustering score: what % of reviews came on high-volume days
    high_volume_reviews = sum(c for _, c in date_counts.items() if c >= 3)
    clustering_score = high_volume_reviews / len(dates) if dates else 0

    return {
        "clustered_dates": clustered,
        "max_same_day": max_same_day,
        "clustering_score": round(clustering_score, 2),
    }


def compute_metrics(reviews_low: list[dict], reviews_high: list[dict], venue_type: str = VENUE_TYPE_GENERAL) -> dict:
    """
    Compute all metrics from stratified reviews.

    Args:
        reviews_low: Reviews sorted by lowest rating
        reviews_high: Reviews sorted by highest rating
        venue_type: Type of venue for venue-specific analysis

    Returns:
        Comprehensive metrics dict for Claude analysis
    """
    # Analyze individual reviews with venue-specific keywords
    analyzed_low = [analyze_review(r, venue_type) for r in reviews_low]
    analyzed_high = [analyze_review(r, venue_type) for r in reviews_high]

    # === CREDIBILITY ANALYSIS ===

    # Average credibility by rating group
    low_credibility_scores = [a["credibility"]["score"] for a in analyzed_low]
    high_credibility_scores = [a["credibility"]["score"] for a in analyzed_high]

    avg_credibility_low = sum(low_credibility_scores) / len(low_credibility_scores) if low_credibility_scores else 0
    avg_credibility_high = sum(high_credibility_scores) / len(high_credibility_scores) if high_credibility_scores else 0

    # Credibility gap: positive = low-rating reviewers more credible (suspicious)
    credibility_gap = avg_credibility_low - avg_credibility_high

    # Local guide distribution
    local_guides_in_low = sum(1 for a in analyzed_low if a["credibility"]["is_local_guide"])
    local_guides_in_high = sum(1 for a in analyzed_high if a["credibility"]["is_local_guide"])

    # === KEYWORD ANALYSIS ===

    # Trap awareness in negative reviews
    reviews_mentioning_trap = sum(1 for a in analyzed_low if a["trap_keywords"])
    reviews_mentioning_manipulation = sum(1 for a in analyzed_low if a["manipulation_keywords"])
    reviews_mentioning_quality = sum(1 for a in analyzed_low if a["quality_keywords"])

    # Collect all mentioned keywords
    all_trap_keywords = []
    all_manipulation_keywords = []
    for a in analyzed_low:
        all_trap_keywords.extend(a["trap_keywords"])
        all_manipulation_keywords.extend(a["manipulation_keywords"])

    # === PHOTO ANALYSIS ===

    # Reviews with photos by rating
    photos_in_low = sum(1 for a in analyzed_low if a["has_images"])
    photos_in_high = sum(1 for a in analyzed_high if a["has_images"])

    photo_rate_low = photos_in_low / len(analyzed_low) if analyzed_low else 0
    photo_rate_high = photos_in_high / len(analyzed_high) if analyzed_high else 0

    # === SERVICE VS FOOD DISPARITY ===

    # Look for pattern: high service rating but low food rating
    disparity_reviews = [a for a in analyzed_low if a["service_food_gap"] and a["service_food_gap"] >= 2]

    # === DATE CLUSTERING (on high ratings - where fake reviews would be) ===

    date_clustering = analyze_date_clustering(reviews_high)

    # === ENGAGEMENT METRICS ===

    # Likes on negative reviews (community validation)
    total_likes_low = sum(a["likes"] for a in analyzed_low)
    avg_likes_low = total_likes_low / len(analyzed_low) if analyzed_low else 0

    # === LANGUAGE ANALYSIS (positive vs negative separately) ===

    lang_positive = analyze_language_distribution(reviews_high)
    lang_negative = analyze_language_distribution(reviews_low)

    # === SPECIFICITY ANALYSIS (for positive reviews) ===

    # Compute specificity scores for high-rated reviews with venue-specific indicators
    for i, r in enumerate(reviews_high):
        text = r.get("text") or r.get("snippet") or ""
        if i < len(analyzed_high):
            analyzed_high[i]["specificity_score"] = compute_specificity(text, venue_type)

    avg_specificity_high = (
        sum(a.get("specificity_score", 50) for a in analyzed_high) / len(analyzed_high)
        if analyzed_high else 50
    )

    # === COMPUTE TRAP SIGNALS ===

    signals = []

    if credibility_gap > 10:
        signals.append({
            "signal": "credibility_inversion",
            "severity": "high" if credibility_gap > 20 else "medium",
            "detail": f"Negative reviewers are more credible (gap: +{credibility_gap:.0f} points)",
        })

    if reviews_mentioning_trap >= 3:
        signals.append({
            "signal": "explicit_trap_warnings",
            "severity": "high",
            "detail": f"{reviews_mentioning_trap} reviews explicitly warn about tourist trap",
            "keywords": list(set(all_trap_keywords)),
        })

    if reviews_mentioning_manipulation >= 2:
        signals.append({
            "signal": "manipulation_accusations",
            "severity": "high",
            "detail": f"{reviews_mentioning_manipulation} reviews mention fake/bought reviews",
            "keywords": list(set(all_manipulation_keywords)),
        })

    if date_clustering["clustering_score"] > 0.3:
        signals.append({
            "signal": "review_clustering",
            "severity": "medium",
            "detail": f"{date_clustering['clustering_score']*100:.0f}% of positive reviews posted on high-volume days",
            "dates": date_clustering["clustered_dates"],
        })

    if photo_rate_low > photo_rate_high + 0.2:
        signals.append({
            "signal": "photo_credibility_gap",
            "severity": "medium",
            "detail": f"Negative reviews have more photos ({photo_rate_low*100:.0f}% vs {photo_rate_high*100:.0f}%)",
        })

    if local_guides_in_low > local_guides_in_high:
        signals.append({
            "signal": "local_guide_warnings",
            "severity": "medium",
            "detail": f"More Local Guides in negative reviews ({local_guides_in_low}) than positive ({local_guides_in_high})",
        })

    # Only add service_food_disparity signal for restaurants
    if venue_type == VENUE_TYPE_RESTAURANT and len(disparity_reviews) >= 2:
        signals.append({
            "signal": "service_food_disparity",
            "severity": "medium",
            "detail": f"{len(disparity_reviews)} reviews rate service high but food low",
        })

    # === LANGUAGE-BASED SIGNALS ===

    # Signal: Tourists dominate positive reviews, locals dominate negative
    if (lang_positive.get("detected") and lang_negative.get("detected") and
        lang_positive.get("tourist_language_pct", 0) > 70 and
        lang_negative.get("tourist_language_pct", 100) < 50):
        signals.append({
            "signal": "language_credibility_split",
            "severity": "high",
            "detail": f"Positive reviews: {lang_positive['tourist_language_pct']}% tourist languages, Negative: {lang_negative['tourist_language_pct']}%",
        })

    # Signal: Low specificity in positive reviews (generic praise)
    if avg_specificity_high < 40:
        signals.append({
            "signal": "generic_positive_reviews",
            "severity": "medium",
            "detail": f"Positive reviews lack specific details (avg specificity: {avg_specificity_high:.0f}/100)",
        })

    # === EXTRACT KEY REVIEWS FOR CLAUDE ===

    # Get the most credible negative reviews for Claude to analyze
    credible_negative = sorted(analyzed_low, key=lambda x: x["credibility"]["score"], reverse=True)[:10]

    # Get the most credible positive reviews for Claude to analyze (NEW)
    credible_positive = sorted(analyzed_high, key=lambda x: x["credibility"]["score"], reverse=True)[:10]

    return {
        "summary": {
            "total_low_rating_reviews": len(reviews_low),
            "total_high_rating_reviews": len(reviews_high),
            "avg_credibility_low_rating": round(avg_credibility_low, 1),
            "avg_credibility_high_rating": round(avg_credibility_high, 1),
            "credibility_gap": round(credibility_gap, 1),
            "local_guides_in_negative": local_guides_in_low,
            "local_guides_in_positive": local_guides_in_high,
            "trap_warning_count": reviews_mentioning_trap,
            "manipulation_accusation_count": reviews_mentioning_manipulation,
            "quality_complaint_count": reviews_mentioning_quality,
            "avg_specificity_positive": round(avg_specificity_high, 1),
        },
        "signals": signals,
        "date_clustering": date_clustering,
        "language_analysis": {
            "positive_reviews": lang_positive,
            "negative_reviews": lang_negative,
        },
        "credible_negative_reviews": [
            {
                "text": reviews_low[i].get("text") or reviews_low[i].get("snippet"),
                "rating": analyzed_low[i]["rating"],
                "credibility_score": analyzed_low[i]["credibility"]["score"],
                "is_local_guide": analyzed_low[i]["credibility"]["is_local_guide"],
                "reviewer_total_reviews": analyzed_low[i]["credibility"]["reviews_count"],
                "trap_keywords": analyzed_low[i]["trap_keywords"],
                "manipulation_keywords": analyzed_low[i]["manipulation_keywords"],
            }
            for i, a in enumerate(credible_negative[:10])
            if i < len(reviews_low)
        ],
        "credible_positive_reviews": [
            {
                "text": reviews_high[i].get("text") or reviews_high[i].get("snippet"),
                "rating": analyzed_high[i]["rating"],
                "credibility_score": analyzed_high[i]["credibility"]["score"],
                "is_local_guide": analyzed_high[i]["credibility"]["is_local_guide"],
                "reviewer_total_reviews": analyzed_high[i]["credibility"]["reviews_count"],
                "specificity_score": analyzed_high[i].get("specificity_score", 50),
            }
            for i, a in enumerate(credible_positive[:10])
            if i < len(reviews_high)
        ],
    }
