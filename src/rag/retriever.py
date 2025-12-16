"""
RAG Retriever for TrapCheck

Provides similar venue examples for few-shot context in the analyzer.
Uses ChromaDB for vector storage and sentence-transformers for embeddings.

Note: This module requires native libraries (libz, libstdc++). If you encounter
import errors, see src/lib_setup.py for configuration options or run:
    python -m src.lib_setup --help-setup
"""

import json
from pathlib import Path
from typing import Optional

# Setup library paths for native dependencies (ChromaDB, sentence-transformers)
# This must happen before importing those libraries
# ensure_library_paths will auto-restart Python with correct LD_LIBRARY_PATH if needed
from src.lib_setup import ensure_library_paths
ensure_library_paths()

# Lazy imports to avoid loading heavy dependencies until needed
_embedder = None
_collection = None
_entries_cache = None


def _get_embedder():
    """Lazy-load the sentence transformer model."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer
        print("Loading embedding model...")
        _embedder = SentenceTransformer('all-MiniLM-L6-v2')
    return _embedder


def _get_collection():
    """Lazy-load and build the ChromaDB collection."""
    global _collection, _entries_cache

    if _collection is not None:
        return _collection, _entries_cache

    import chromadb

    # Load RAG database
    rag_path = Path(__file__).parent / "data" / "rag_master.json"
    if not rag_path.exists():
        raise FileNotFoundError(f"RAG database not found: {rag_path}")

    print(f"Loading RAG database from {rag_path}...")
    with open(rag_path) as f:
        data = json.load(f)

    entries = data["entries"]
    _entries_cache = {e["id"]: e for e in entries}

    # Initialize ChromaDB (ephemeral for now)
    client = chromadb.Client()

    # Check if collection exists, delete if so (for fresh start)
    try:
        client.delete_collection("tourist_trap_examples")
    except Exception:
        pass

    _collection = client.create_collection(
        name="tourist_trap_examples",
        metadata={"hnsw:space": "cosine"}
    )

    # Prepare data for batch insert
    ids = [e["id"] for e in entries]
    texts = [e["embedding_text"] for e in entries]
    metadatas = [{
        "name": e["name"],
        "location": e["location"],
        "city": e.get("city", ""),
        "country": e.get("country", ""),
        "category": e["category"],
        "verdict": e["verdict"],
        "score": e["tourist_trap_score"],
        "confidence": e["confidence"],
        "price_tier": e.get("price_tier", ""),
        "summary": e["summary"][:500],  # Truncate for metadata
    } for e in entries]

    # Generate embeddings
    print(f"Generating embeddings for {len(entries)} entries...")
    embedder = _get_embedder()
    embeddings = embedder.encode(texts, show_progress_bar=True).tolist()

    # Add to collection
    _collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=texts
    )

    print(f"RAG database loaded: {len(entries)} entries indexed")
    return _collection, _entries_cache


# Map venue_type to RAG categories
VENUE_TYPE_TO_RAG_CATEGORIES = {
    "restaurant": ["restaurant", "cafe", "bar", "street_food"],
    "museum": ["attraction", "museum"],
    "attraction": ["attraction", "museum"],
    "tour": ["attraction", "tour"],
    "shop": ["market", "shop"],
    "general": None,  # No filter, use all
}


def retrieve_similar(
    query: str,
    n: int = 3,
    verdict_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    venue_type: Optional[str] = None,
) -> list[dict]:
    """
    Retrieve similar venues from the RAG database.

    Args:
        query: Search query (venue name, type, location, etc.)
        n: Number of results to return
        verdict_filter: Filter by verdict ("tourist_trap", "local_gem", "mixed")
        category_filter: Filter by category ("restaurant", "cafe", "bar", etc.)
        venue_type: Filter by venue type (maps to relevant RAG categories)

    Returns:
        List of similar venue metadata dicts
    """
    collection, entries = _get_collection()
    embedder = _get_embedder()

    # Generate query embedding
    query_embedding = embedder.encode(query).tolist()

    # Resolve category filter from venue_type if provided
    effective_categories = None
    if category_filter:
        effective_categories = [category_filter]
    elif venue_type and venue_type in VENUE_TYPE_TO_RAG_CATEGORIES:
        effective_categories = VENUE_TYPE_TO_RAG_CATEGORIES[venue_type]

    # Build filter
    where = None
    if verdict_filter and effective_categories and len(effective_categories) > 0:
        where = {"$and": [
            {"verdict": verdict_filter},
            {"category": {"$in": effective_categories}}
        ]}
    elif verdict_filter:
        where = {"verdict": verdict_filter}
    elif effective_categories and len(effective_categories) > 0:
        where = {"category": {"$in": effective_categories}}

    # Query collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        where=where
    )

    # Format results
    output = []
    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]
        doc_id = results["ids"][0][i]
        distance = results["distances"][0][i] if results.get("distances") else None

        # Get full entry for additional details
        full_entry = entries.get(doc_id, {})

        output.append({
            "id": doc_id,
            "name": metadata["name"],
            "location": metadata["location"],
            "category": metadata["category"],
            "verdict": metadata["verdict"],
            "score": metadata["score"],
            "confidence": metadata["confidence"],
            "price_tier": metadata.get("price_tier", ""),
            "summary": metadata["summary"],
            "distance": distance,
            # Additional fields from full entry
            "red_flags": full_entry.get("red_flags", [])[:2],  # Top 2
            "positive_signals": full_entry.get("positive_signals", [])[:2],
        })

    return output


def retrieve_calibration_examples(
    query: str,
    category: Optional[str] = None,
    venue_type: Optional[str] = None,
    n_per_verdict: int = 2
) -> dict:
    """
    Retrieve a balanced set of examples for score calibration.

    Returns examples from each verdict category to give the LLM
    reference points for scoring.

    Args:
        query: Search query
        category: Optional category filter (takes precedence over venue_type)
        venue_type: Optional venue type filter (maps to relevant RAG categories)
        n_per_verdict: Number of examples per verdict type

    Returns:
        Dict with 'traps', 'gems', and 'mixed' lists
    """
    traps = retrieve_similar(query, n=n_per_verdict, verdict_filter="tourist_trap", category_filter=category, venue_type=venue_type)
    gems = retrieve_similar(query, n=n_per_verdict, verdict_filter="local_gem", category_filter=category, venue_type=venue_type)
    mixed = retrieve_similar(query, n=n_per_verdict, verdict_filter="mixed", category_filter=category, venue_type=venue_type)

    return {
        "traps": traps,
        "gems": gems,
        "mixed": mixed,
        "total": len(traps) + len(gems) + len(mixed)
    }


def format_examples_for_prompt(examples: dict) -> str:
    """
    Format retrieved examples as text for inclusion in the LLM prompt.

    Args:
        examples: Dict from retrieve_calibration_examples()

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
    lines.append("## Scoring Guide (start at 25, add ONLY for trap indicators)")
    lines.append("- 70-100: 🚨 TOURIST TRAP - Clear exploitation (fake reviews, scams, ripoffs)")
    lines.append("- 50-69: ⚠️ MIXED - Some trap concerns worth noting")
    lines.append("- 0-49: ✓ NOT A TRAP - No significant trap indicators")
    lines.append("")
    lines.append("**ONLY increase score for:** explicit 'tourist trap' warnings, fake review accusations, price+quality complaints together")
    lines.append("**DO NOT increase for:** service issues, crowds, waits, location, high prices alone")
    lines.append("")

    return "\n".join(lines)


# Simple test
if __name__ == "__main__":
    print("Testing RAG retriever...")

    # Test similarity search
    results = retrieve_similar("Italian restaurant Rome tourist location", n=3)
    print("\n--- Similar venues ---")
    for r in results:
        print(f"  {r['name']} ({r['location']}): {r['score']}/100 [{r['verdict']}]")

    # Test calibration examples
    examples = retrieve_calibration_examples("pizza restaurant Naples", category="restaurant")
    print(f"\n--- Calibration examples ({examples['total']} total) ---")

    prompt_text = format_examples_for_prompt(examples)
    print("\n--- Formatted for prompt ---")
    print(prompt_text[:1000] + "..." if len(prompt_text) > 1000 else prompt_text)
