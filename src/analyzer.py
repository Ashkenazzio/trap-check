"""
Core tourist trap analyzer using computed metrics + Google AI API.
"""
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import httpx
from src.config import GOOGLE_API_KEY, SERPAPI_KEY
from src.tools.serpapi import search_place, fetch_stratified_reviews
from src.tools.web_search import search_external_opinions, check_tourist_proximity, get_mock_web_search, get_mock_proximity
from src.metrics import compute_metrics

USE_MOCK = not SERPAPI_KEY


def _get_venue_key(query: str) -> str:
    """Convert venue query to mock data key."""
    query_lower = query.lower()
    if "michele" in query_lower:
        return "da_michele"
    elif "olive garden" in query_lower:
        return "olive_garden_times_square"
    elif "katz" in query_lower:
        return "katzs_deli"
    elif "carlo menta" in query_lower:
        return "carlo_menta"
    return "unknown"


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"

SYSTEM_PROMPT = """You are an expert tourist trap analyst. Based on pre-computed metrics and review samples, provide a CONCISE assessment.

## Scoring Guidelines
- credibility_inversion = strong trap signal
- explicit_trap_warnings = very strong signal
- manipulation_accusations = critical signal
- review_clustering = manipulation indicator
- local_guide_warnings = trust their assessment
- language_credibility_split = strong trap signal
- generic_positive_reviews = suspicious pattern

## Response Guidelines
- verdict: ONE clear sentence (max 20 words)
- recommendation: 2-3 actionable sentences for travelers
- reasoning: 1 focused paragraph (max 150 words) - hit the key points, skip obvious details
- key_concerns: max 3 items, brief evidence quotes
- mitigating_factors: max 3 items, brief phrases"""

# JSON schema for structured output
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "tourist_trap_score": {
            "type": "integer",
            "description": "Score from 0-100 indicating likelihood of being a tourist trap"
        },
        "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"]
        },
        "classification": {
            "type": "string",
            "enum": ["definite_trap", "likely_trap", "possibly_trap", "unclear", "likely_authentic", "verified_authentic"]
        },
        "verdict": {
            "type": "string",
            "description": "One sentence summary"
        },
        "key_concerns": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "concern": {"type": "string"},
                    "evidence": {"type": "string"}
                },
                "required": ["concern", "evidence"]
            }
        },
        "mitigating_factors": {
            "type": "array",
            "items": {"type": "string"}
        },
        "recommendation": {
            "type": "string",
            "description": "Advice for tourists"
        },
        "reasoning": {
            "type": "string",
            "description": "1 paragraph analysis, max 150 words"
        }
    },
    "required": ["tourist_trap_score", "confidence", "classification", "verdict", "key_concerns", "mitigating_factors", "recommendation", "reasoning"]
}


def analyze_venue(query: str, location: str | None = None) -> dict:
    """
    Analyze a venue for tourist trap indicators using metrics + Claude.

    Args:
        query: Business name or Google Maps URL
        location: City/region (optional if URL provided)

    Returns:
        Analysis result dict
    """
    # Step 1: Search for the place
    print(f"Searching for: {query}" + (f" in {location}" if location else ""))
    place = search_place(query, location)

    if not place:
        return {"error": f"Could not find place: {query}"}

    print(f"Found: {place['name']} ({place['rating']}* from {place['review_count']} reviews)")

    # Step 2: Fetch stratified reviews
    if not place.get("data_id"):
        return {"error": "No data_id available for this place"}

    print("Fetching reviews (lowest and highest rated)...")
    review_data = fetch_stratified_reviews(place["data_id"], reviews_per_tier=30)

    reviews_low = review_data.get("reviews_low", [])
    reviews_high = review_data.get("reviews_high", [])
    print(f"Retrieved {len(reviews_low)} low-rated + {len(reviews_high)} high-rated reviews")

    # Step 3: Compute metrics BEFORE Claude sees anything
    print("Computing metrics...")
    metrics = compute_metrics(reviews_low, reviews_high)

    # Step 4: Get external signals (web search + proximity) - run in PARALLEL
    print("Fetching external signals (parallel)...")
    if USE_MOCK:
        venue_key = _get_venue_key(query)
        external_opinions = get_mock_web_search(venue_key)
        proximity_data = get_mock_proximity(venue_key)
    else:
        # Run both API calls in parallel to save ~5-10 seconds
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_opinions = executor.submit(
                search_external_opinions, place["name"], location or ""
            )
            future_proximity = executor.submit(
                check_tourist_proximity,
                place["name"],
                place.get("address", ""),
                location or ""
            )
            external_opinions = future_opinions.result()
            proximity_data = future_proximity.result()

    print(f"External: Reddit={external_opinions.get('reddit_sentiment', 'N/A')}, Proximity={proximity_data.get('proximity_score', 'N/A')}/100")

    # Add proximity-based signal if applicable
    if proximity_data.get("proximity_score", 0) > 70:
        metrics["signals"].append({
            "signal": "tourist_hotspot_location",
            "severity": "medium",
            "detail": f"Located in high-tourist area (score: {proximity_data['proximity_score']}/100) near {', '.join(proximity_data.get('near_attractions', [])[:3])}"
        })

    # Add external opinion signal if negative sentiment dominates
    neg_sentiments = sum(1 for s in [
        external_opinions.get("reddit_sentiment"),
        external_opinions.get("tripadvisor_sentiment"),
        external_opinions.get("blog_sentiment")
    ] if s == "negative")

    if neg_sentiments >= 2 or external_opinions.get("external_warnings", 0) >= 5:
        metrics["signals"].append({
            "signal": "external_negative_reputation",
            "severity": "high",
            "detail": f"Negative sentiment on external platforms. Warnings: {external_opinions.get('external_warnings', 0)}, Reddit: {external_opinions.get('reddit_sentiment', 'none')}"
        })

    # Step 5: Prepare context for Gemini
    print("Analyzing with Gemini...")

    prompt = f"""## VENUE INFORMATION
Name: {place['name']}
Address: {place['address']}
Overall Rating: {place['rating']} stars
Total Reviews: {place['review_count']}
Price Level: {place['price_level'] or 'Not specified'}
Type: {place['type']}

## COMPUTED SIGNALS

### Summary Metrics
- Low-rating reviews analyzed: {metrics['summary']['total_low_rating_reviews']}
- High-rating reviews analyzed: {metrics['summary']['total_high_rating_reviews']}
- Average credibility of negative reviewers: {metrics['summary']['avg_credibility_low_rating']}/100
- Average credibility of positive reviewers: {metrics['summary']['avg_credibility_high_rating']}/100
- Credibility gap: {metrics['summary']['credibility_gap']:+.1f} (positive = negative reviewers more credible)
- Local Guides in negative reviews: {metrics['summary']['local_guides_in_negative']}
- Local Guides in positive reviews: {metrics['summary']['local_guides_in_positive']}
- Reviews explicitly warning "tourist trap": {metrics['summary']['trap_warning_count']}
- Reviews accusing fake/bought reviews: {metrics['summary']['manipulation_accusation_count']}
- Reviews with quality complaints: {metrics['summary']['quality_complaint_count']}
- Average specificity of positive reviews: {metrics['summary'].get('avg_specificity_positive', 'N/A')}/100

### Detected Signals
{json.dumps(metrics['signals'], indent=2) if metrics['signals'] else "No significant signals detected"}

### Review Date Clustering (in positive reviews)
{json.dumps(metrics['date_clustering'], indent=2)}

### Language Analysis
{json.dumps(metrics.get('language_analysis', {}), indent=2)}

## EXTERNAL SIGNALS (Web Search Results)

### Location Analysis
- Tourist Hotspot: {'Yes' if proximity_data.get('is_tourist_hotspot') else 'No'}
- Proximity Score: {proximity_data.get('proximity_score', 'N/A')}/100
- Nearby Attractions: {', '.join(proximity_data.get('near_attractions', [])) or 'None identified'}
- Assessment: {proximity_data.get('reasoning', 'N/A')}

### External Opinions (Reddit, TripAdvisor Forums, Food Blogs)
- Reddit Sentiment: {external_opinions.get('reddit_sentiment', 'none')}
- TripAdvisor Forum Sentiment: {external_opinions.get('tripadvisor_sentiment', 'none')}
- Food Blog Sentiment: {external_opinions.get('blog_sentiment', 'none')}
- External Warnings: {external_opinions.get('external_warnings', 0)}
- External Recommendations: {external_opinions.get('external_recommendations', 0)}
- Summary: {external_opinions.get('summary', 'No data')}
- Notable Quotes: {json.dumps(external_opinions.get('notable_quotes', []), indent=2)}

## MOST CREDIBLE NEGATIVE REVIEWS

These are the negative reviews from the most experienced/trustworthy reviewers:

"""

    for i, review in enumerate(metrics['credible_negative_reviews'][:5], 1):
        prompt += f"""
### Review {i}
- Rating: {review['rating']}/5
- Reviewer credibility: {review['credibility_score']}/100
- Local Guide: {'Yes' if review['is_local_guide'] else 'No'}
- Reviewer's total reviews: {review['reviewer_total_reviews']}
- Trap keywords found: {review['trap_keywords'] or 'None'}
- Manipulation keywords: {review['manipulation_keywords'] or 'None'}
- Text: "{review['text'][:300]}{'...' if len(review['text'] or '') > 300 else ''}"
"""

    # Add credible positive reviews section
    prompt += """
## MOST CREDIBLE POSITIVE REVIEWS

Assess whether these are genuine detailed praise or vague/generic.
Higher specificity scores indicate more detailed, specific reviews.

"""

    for i, review in enumerate(metrics.get('credible_positive_reviews', [])[:3], 1):
        text = review.get('text') or ''
        prompt += f"""
### Positive Review {i}
- Rating: {review['rating']}/5
- Reviewer credibility: {review['credibility_score']}/100
- Specificity score: {review.get('specificity_score', 'N/A')}/100
- Local Guide: {'Yes' if review['is_local_guide'] else 'No'}
- Reviewer's total reviews: {review['reviewer_total_reviews']}
- Text: "{text[:250]}{'...' if len(text) > 250 else ''}"
"""

    prompt += "\n\nBased on these metrics and reviews, provide your analysis."

    full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

    # Call Gemini REST API with structured JSON output
    response = httpx.post(
        GEMINI_API_URL,
        params={"key": GOOGLE_API_KEY},
        json={
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json",
                "responseSchema": RESPONSE_SCHEMA
            }
        },
        timeout=60.0
    )
    response.raise_for_status()
    result = response.json()

    # Extract and parse JSON response (guaranteed to be valid JSON with schema)
    response_text = result["candidates"][0]["content"]["parts"][0]["text"]

    try:
        analysis = json.loads(response_text)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse analysis: {e}", "raw_response": response_text}

    # Add metadata and metrics
    analysis["meta"] = {
        "query": query,
        "location": location,
        "place_name": place["name"],
        "place_address": place["address"],
        "place_rating": place["rating"],
        "place_review_count": place["review_count"],
        "google_maps_url": place["google_maps_url"],
        "reviews_analyzed": len(reviews_low) + len(reviews_high),
    }
    analysis["computed_metrics"] = metrics["summary"]
    analysis["signals"] = metrics["signals"]
    analysis["external_signals"] = {
        "proximity": proximity_data,
        "external_opinions": external_opinions,
    }
    analysis["language_analysis"] = metrics.get("language_analysis", {})

    return analysis


def format_analysis(analysis: dict) -> str:
    """Format analysis result for console output."""
    if "error" in analysis:
        return f"Error: {analysis['error']}"

    output = []
    output.append("=" * 70)
    output.append(f"TOURIST TRAP ANALYSIS: {analysis['meta']['place_name']}")
    output.append(f"Rating: {analysis['meta']['place_rating']}* | Reviews: {analysis['meta']['place_review_count']}")
    output.append("=" * 70)
    output.append("")

    # Verdict
    score = analysis.get("tourist_trap_score", "N/A")
    classification = analysis.get("classification", "N/A")
    confidence = analysis.get("confidence", "N/A")

    output.append(f"TRAP SCORE: {score}/100 [{classification.upper()}]")
    output.append(f"Confidence: {confidence}")
    output.append(f"Verdict: {analysis.get('verdict', 'N/A')}")
    output.append("")

    # Computed signals
    if analysis.get("signals"):
        output.append("DETECTED SIGNALS:")
        for signal in analysis["signals"]:
            severity = signal.get("severity", "medium").upper()
            output.append(f"  [{severity}] {signal['signal']}: {signal['detail']}")
        output.append("")

    # Key concerns
    concerns = analysis.get("key_concerns", [])
    if concerns:
        output.append("KEY CONCERNS:")
        for c in concerns:
            output.append(f"  - {c['concern']}")
            output.append(f"    Evidence: {c['evidence'][:100]}...")
        output.append("")

    # Mitigating factors
    mitigating = analysis.get("mitigating_factors", [])
    if mitigating:
        output.append("MITIGATING FACTORS:")
        for m in mitigating:
            output.append(f"  + {m}")
        output.append("")

    # Recommendation
    output.append(f"RECOMMENDATION: {analysis.get('recommendation', 'N/A')}")
    output.append("")

    # Reasoning
    output.append("ANALYSIS:")
    output.append(analysis.get("reasoning", "N/A"))
    output.append("")
    output.append(f"Google Maps: {analysis['meta'].get('google_maps_url', 'N/A')}")

    return "\n".join(output)
