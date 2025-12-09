"""
Metrics computation layer for tourist trap detection.
Computes quantitative signals from raw review data BEFORE Claude analysis.
"""
import re
from collections import Counter
from datetime import datetime


# Keywords that indicate awareness of tourist trap behavior (in negative reviews)
TRAP_AWARENESS_KEYWORDS = [
    "tourist trap", "trap", "fake review", "bought review", "scam",
    "avoid", "don't go", "do not go", "stay away", "waste of money",
    "rip off", "ripoff", "overpriced", "not worth",
]

# Keywords suggesting review manipulation
MANIPULATION_KEYWORDS = [
    "fake", "bought", "paid review", "forced to review", "asked for review",
    "in exchange", "free dessert", "free drink",
]

# Quality complaint keywords
QUALITY_KEYWORDS = [
    "disgusting", "terrible", "awful", "worst", "horrible", "inedible",
    "sick", "food poisoning", "diarrhea", "stomach", "bland", "tasteless",
    "frozen", "microwave", "premade", "pre-made", "canned",
]


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


def analyze_review(review: dict) -> dict:
    """
    Analyze a single review and extract all metrics.
    """
    text = review.get("text") or review.get("snippet") or ""
    rating = review.get("rating") or 0
    user = review.get("user") or {}

    credibility = compute_reviewer_credibility(user)

    # Keyword detection
    trap_keywords = detect_keywords(text, TRAP_AWARENESS_KEYWORDS)
    manipulation_keywords = detect_keywords(text, MANIPULATION_KEYWORDS)
    quality_keywords = detect_keywords(text, QUALITY_KEYWORDS)

    # Check for photos in this review
    has_images = bool(review.get("images"))

    # Sub-ratings (food, service, atmosphere)
    details = review.get("details") or {}
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
    service_food_gap = None
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


def compute_metrics(reviews_low: list[dict], reviews_high: list[dict]) -> dict:
    """
    Compute all metrics from stratified reviews.

    Args:
        reviews_low: Reviews sorted by lowest rating
        reviews_high: Reviews sorted by highest rating

    Returns:
        Comprehensive metrics dict for Claude analysis
    """
    # Analyze individual reviews
    analyzed_low = [analyze_review(r) for r in reviews_low]
    analyzed_high = [analyze_review(r) for r in reviews_high]

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

    if len(disparity_reviews) >= 2:
        signals.append({
            "signal": "service_food_disparity",
            "severity": "medium",
            "detail": f"{len(disparity_reviews)} reviews rate service high but food low",
        })

    # === EXTRACT KEY NEGATIVE REVIEWS FOR CLAUDE ===

    # Get the most credible negative reviews for Claude to analyze
    credible_negative = sorted(analyzed_low, key=lambda x: x["credibility"]["score"], reverse=True)[:10]

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
        },
        "signals": signals,
        "date_clustering": date_clustering,
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
    }
