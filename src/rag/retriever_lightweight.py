"""
Lightweight RAG Retriever for TrapCheck

Simple keyword-based retriever that doesn't require ChromaDB or sentence-transformers.
Uses category/venue-type filtering and keyword overlap scoring.

This is a simpler alternative to the vector-based retriever for environments
where native library dependencies are problematic.
"""

import json
import re
from pathlib import Path
from typing import Optional
from collections import Counter


# Cache for loaded entries
_entries_cache = None
_entries_by_category = None
_entries_by_verdict = None


def _load_rag_database():
    """Load and index the RAG database."""
    global _entries_cache, _entries_by_category, _entries_by_verdict

    if _entries_cache is not None:
        return _entries_cache

    rag_path = Path(__file__).parent / "data" / "rag_master.json"
    if not rag_path.exists():
        raise FileNotFoundError(f"RAG database not found: {rag_path}")

    with open(rag_path) as f:
        data = json.load(f)

    entries = data["entries"]
    _entries_cache = {e["id"]: e for e in entries}

    # Index by category
    _entries_by_category = {}
    for e in entries:
        cat = e.get("category", "general")
        if cat not in _entries_by_category:
            _entries_by_category[cat] = []
        _entries_by_category[cat].append(e)

    # Index by verdict
    _entries_by_verdict = {}
    for e in entries:
        verdict = e.get("verdict", "mixed")
        if verdict not in _entries_by_verdict:
            _entries_by_verdict[verdict] = []
        _entries_by_verdict[verdict].append(e)

    return _entries_cache


def _extract_keywords(text: str) -> set[str]:
    """Extract keywords from text for matching."""
    # Lowercase and extract words
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    # Filter out common stopwords
    stopwords = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had',
        'her', 'was', 'one', 'our', 'out', 'has', 'have', 'been', 'were',
        'they', 'this', 'that', 'with', 'from', 'your', 'will', 'more',
        'when', 'very', 'just', 'about', 'also', 'some', 'what', 'there',
        'than', 'into', 'them', 'would', 'could', 'which', 'their', 'other'
    }
    return set(w for w in words if w not in stopwords)


def _keyword_similarity(query_keywords: set[str], entry: dict) -> float:
    """Score similarity based on keyword overlap."""
    # Get keywords from entry's embedding_text and summary
    entry_text = entry.get("embedding_text", "") + " " + entry.get("summary", "")
    entry_keywords = _extract_keywords(entry_text)

    # Also include name and location
    name_keywords = _extract_keywords(entry.get("name", ""))
    location_keywords = _extract_keywords(entry.get("location", ""))
    entry_keywords.update(name_keywords)
    entry_keywords.update(location_keywords)

    if not entry_keywords or not query_keywords:
        return 0.0

    # Jaccard-like similarity
    intersection = len(query_keywords & entry_keywords)
    union = len(query_keywords | entry_keywords)

    return intersection / union if union > 0 else 0.0


# Map venue_type to RAG categories (same as vector retriever)
VENUE_TYPE_TO_RAG_CATEGORIES = {
    "restaurant": ["restaurant", "cafe", "bar", "street_food"],
    "museum": ["attraction", "museum"],
    "attraction": ["attraction", "museum"],
    "tour": ["attraction", "tour"],
    "shop": ["market", "shop"],
    "general": None,  # No filter, use all
}


def retrieve_similar_lightweight(
    query: str,
    n: int = 3,
    verdict_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    venue_type: Optional[str] = None,
) -> list[dict]:
    """
    Retrieve similar venues using keyword matching.

    Args:
        query: Search query (venue name, type, location, etc.)
        n: Number of results to return
        verdict_filter: Filter by verdict ("tourist_trap", "local_gem", "mixed")
        category_filter: Filter by category ("restaurant", "cafe", "bar", etc.)
        venue_type: Filter by venue type (maps to relevant RAG categories)

    Returns:
        List of similar venue metadata dicts
    """
    _load_rag_database()

    query_keywords = _extract_keywords(query)

    # Resolve category filter from venue_type if provided
    effective_categories = None
    if category_filter:
        effective_categories = [category_filter]
    elif venue_type and venue_type in VENUE_TYPE_TO_RAG_CATEGORIES:
        effective_categories = VENUE_TYPE_TO_RAG_CATEGORIES[venue_type]

    # Get candidate entries
    candidates = []

    if verdict_filter and verdict_filter in _entries_by_verdict:
        # Start with verdict-filtered entries
        candidates = list(_entries_by_verdict[verdict_filter])
    else:
        # All entries
        candidates = list(_entries_cache.values())

    # Filter by category if specified
    if effective_categories:
        candidates = [e for e in candidates if e.get("category") in effective_categories]

    if not candidates:
        # Fall back to all entries with verdict filter only
        if verdict_filter and verdict_filter in _entries_by_verdict:
            candidates = list(_entries_by_verdict[verdict_filter])
        else:
            candidates = list(_entries_cache.values())

    # Score and rank candidates
    scored = []
    for entry in candidates:
        score = _keyword_similarity(query_keywords, entry)
        scored.append((score, entry))

    # Sort by score (descending) and take top n
    scored.sort(key=lambda x: x[0], reverse=True)
    top_entries = [entry for score, entry in scored[:n]]

    # Format output
    output = []
    for entry in top_entries:
        output.append({
            "id": entry["id"],
            "name": entry["name"],
            "location": entry["location"],
            "category": entry.get("category", "general"),
            "verdict": entry["verdict"],
            "score": entry["tourist_trap_score"],
            "confidence": entry.get("confidence", "medium"),
            "price_tier": entry.get("price_tier", ""),
            "summary": entry.get("summary", "")[:500],
            "distance": None,  # Not applicable for keyword matching
            "red_flags": entry.get("red_flags", [])[:2],
            "positive_signals": entry.get("positive_signals", [])[:2],
        })

    return output


def retrieve_calibration_examples_lightweight(
    query: str,
    category: Optional[str] = None,
    venue_type: Optional[str] = None,
    n_per_verdict: int = 2
) -> dict:
    """
    Retrieve a balanced set of examples for score calibration using keyword matching.

    Args:
        query: Search query
        category: Optional category filter (takes precedence over venue_type)
        venue_type: Optional venue type filter (maps to relevant RAG categories)
        n_per_verdict: Number of examples per verdict type

    Returns:
        Dict with 'traps', 'gems', and 'mixed' lists
    """
    traps = retrieve_similar_lightweight(query, n=n_per_verdict, verdict_filter="tourist_trap", category_filter=category, venue_type=venue_type)
    gems = retrieve_similar_lightweight(query, n=n_per_verdict, verdict_filter="local_gem", category_filter=category, venue_type=venue_type)
    mixed = retrieve_similar_lightweight(query, n=n_per_verdict, verdict_filter="mixed", category_filter=category, venue_type=venue_type)

    return {
        "traps": traps,
        "gems": gems,
        "mixed": mixed,
        "total": len(traps) + len(gems) + len(mixed)
    }


def format_examples_for_prompt(examples: dict) -> str:
    """
    Format retrieved examples as text for inclusion in the LLM prompt.
    Same format as vector retriever for consistency.

    Args:
        examples: Dict from retrieve_calibration_examples_lightweight()

    Returns:
        Formatted string for prompt injection
    """
    lines = ["## REFERENCE EXAMPLES FOR CALIBRATION", ""]
    lines.append("Use these similar venues as reference points for your scoring:")
    lines.append("")

    all_examples = examples["traps"] + examples["gems"] + examples["mixed"]

    if not all_examples:
        return ""

    for ex in all_examples:
        verdict_emoji = {
            "tourist_trap": "🚨",
            "local_gem": "💎",
            "mixed": "🤔"
        }.get(ex["verdict"], "❓")

        lines.append(f"### {verdict_emoji} {ex['name']} ({ex['location']})")
        lines.append(f"- **Score:** {ex['score']}/100")
        lines.append(f"- **Verdict:** {ex['verdict'].replace('_', ' ').title()}")
        lines.append(f"- **Category:** {ex['category']}")
        if ex.get("price_tier"):
            lines.append(f"- **Price:** {ex['price_tier']}")
        lines.append(f"- **Summary:** {ex['summary']}")

        # Add key signals
        if ex.get("red_flags"):
            flags = [f["type"] for f in ex["red_flags"][:2]]
            lines.append(f"- **Red Flags:** {', '.join(flags)}")

        if ex.get("positive_signals"):
            positives = [p["type"] for p in ex["positive_signals"][:2]]
            lines.append(f"- **Positives:** {', '.join(positives)}")

        lines.append("")

    lines.append("---")
    lines.append("Use these examples to calibrate your scoring. A venue similar to the tourist traps above should score 60+, while one similar to local gems should score below 30.")
    lines.append("")

    return "\n".join(lines)


# Simple test
if __name__ == "__main__":
    print("Testing lightweight RAG retriever...")

    # Test similarity search
    results = retrieve_similar_lightweight("Italian restaurant Rome tourist location", n=3)
    print("\n--- Similar venues ---")
    for r in results:
        print(f"  {r['name']} ({r['location']}): {r['score']}/100 [{r['verdict']}]")

    # Test calibration examples
    examples = retrieve_calibration_examples_lightweight("pizza restaurant Naples", category="restaurant")
    print(f"\n--- Calibration examples ({examples['total']} total) ---")

    prompt_text = format_examples_for_prompt(examples)
    print("\n--- Formatted for prompt ---")
    print(prompt_text[:1000] + "..." if len(prompt_text) > 1000 else prompt_text)
