"""
Core tourist trap analyzer using computed metrics + Claude API.
"""
import json
from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY
from src.tools.serpapi import search_place, fetch_stratified_reviews
from src.metrics import compute_metrics

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are an expert analyst helping identify tourist traps based on pre-computed metrics and review data.

You will receive:
1. COMPUTED SIGNALS - Quantitative metrics already extracted from reviews
2. CREDIBLE NEGATIVE REVIEWS - The most trustworthy negative reviews (from experienced reviewers)
3. PLACE METADATA - Basic info about the venue

Your job is to:
1. Interpret the signals and determine if this is a tourist trap
2. Explain the reasoning in a way a traveler would understand
3. Provide an actionable verdict

## Scoring Guidelines

Use the computed signals to inform your score:
- credibility_inversion (negative reviewers more credible) = strong trap signal
- explicit_trap_warnings (reviews calling it a trap) = very strong signal
- manipulation_accusations (fake review claims) = critical signal
- review_clustering (many reviews same day) = manipulation indicator
- local_guide_warnings (Local Guides in negatives) = trust their assessment

## Output Format

Respond with valid JSON only:
{
  "tourist_trap_score": <0-100>,
  "confidence": "<high|medium|low>",
  "classification": "<definite_trap|likely_trap|possibly_trap|unclear|likely_authentic|verified_authentic>",
  "verdict": "<one sentence summary>",
  "key_concerns": [
    {"concern": "<issue>", "evidence": "<specific quote or metric>"}
  ],
  "mitigating_factors": ["<any positives>"],
  "recommendation": "<should a tourist visit? with caveats>",
  "reasoning": "<2-3 paragraph analysis>"
}"""


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

    # Step 4: Prepare context for Claude
    print("Analyzing with Claude...")

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

### Detected Signals
{json.dumps(metrics['signals'], indent=2) if metrics['signals'] else "No significant signals detected"}

### Review Date Clustering (in positive reviews)
{json.dumps(metrics['date_clustering'], indent=2)}

## MOST CREDIBLE NEGATIVE REVIEWS

These are the negative reviews from the most experienced/trustworthy reviewers:

"""

    for i, review in enumerate(metrics['credible_negative_reviews'][:8], 1):
        prompt += f"""
### Review {i}
- Rating: {review['rating']}/5
- Reviewer credibility: {review['credibility_score']}/100
- Local Guide: {'Yes' if review['is_local_guide'] else 'No'}
- Reviewer's total reviews: {review['reviewer_total_reviews']}
- Trap keywords found: {review['trap_keywords'] or 'None'}
- Manipulation keywords: {review['manipulation_keywords'] or 'None'}
- Text: "{review['text'][:500]}{'...' if len(review['text'] or '') > 500 else ''}"
"""

    prompt += "\n\nBased on these metrics and reviews, provide your analysis as JSON."

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse Claude's response
    try:
        analysis = json.loads(response.content[0].text)
    except json.JSONDecodeError:
        text = response.content[0].text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            analysis = json.loads(text[start:end])
        else:
            return {"error": "Failed to parse analysis", "raw_response": text}

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
