"""
Synthetic Analyzer for Testing

Uses RAG entries converted to mock data to test the analysis pipeline
without requiring live API calls.
"""

import json
from typing import Optional
import httpx

from src.config import GOOGLE_API_KEY
from src.metrics import compute_metrics, infer_venue_type
from src.test_harness import (
    load_rag_database,
    rag_entry_to_mock_place,
    rag_entry_to_mock_reviews,
    get_mock_external_signals,
)
from src.analyzer import SYSTEM_PROMPT, RESPONSE_SCHEMA, GEMINI_API_URL


def analyze_synthetic(
    entry: dict,
    exclude_from_rag: bool = True,
    use_rag: bool = True,
    temperature: float = None,
    verbose: bool = False,
) -> dict:
    """
    Analyze a RAG entry using synthetic data.

    Args:
        entry: RAG database entry
        exclude_from_rag: If True, exclude this entry from RAG examples (leave-one-out)
        use_rag: Whether to use RAG calibration examples
        temperature: Gemini temperature (None for default)
        verbose: Print progress

    Returns:
        Analysis result dict with predicted score and metadata
    """
    if verbose:
        print(f"Analyzing: {entry['name']} ({entry['location']})")

    # Convert RAG entry to mock data
    place = rag_entry_to_mock_place(entry)
    reviews_low, reviews_high = rag_entry_to_mock_reviews(entry)
    external_opinions, proximity_data = get_mock_external_signals(entry)

    if verbose:
        print(f"  Mock data: {len(reviews_low)} low + {len(reviews_high)} high reviews")

    # Detect venue type
    venue_type = entry.get("category", "restaurant")
    # Map RAG categories to venue types
    category_to_venue_type = {
        "restaurant": "restaurant",
        "cafe": "restaurant",
        "bar": "restaurant",
        "street_food": "restaurant",
        "attraction": "attraction",
        "museum": "museum",
        "market": "shop",
        "shop": "shop",
        "tour": "tour",
    }
    venue_type = category_to_venue_type.get(venue_type, "restaurant")

    # Get RAG examples (excluding this entry if requested)
    rag_examples = None
    if use_rag:
        from src.rag.retriever_lightweight import (
            retrieve_calibration_examples_lightweight,
            format_examples_for_prompt,
        )

        rag_query = f"{entry['name']} {venue_type} {entry.get('city', '')}"

        if exclude_from_rag:
            # Temporarily get examples then filter out this entry
            examples = retrieve_calibration_examples_lightweight(
                query=rag_query,
                venue_type=venue_type,
                n_per_verdict=3  # Get more so we have enough after filtering
            )
            # Filter out the test entry
            for category in ["traps", "gems", "mixed"]:
                examples[category] = [
                    ex for ex in examples[category]
                    if ex["id"] != entry["id"]
                ][:2]  # Keep only 2 per category
            examples["total"] = sum(len(examples[c]) for c in ["traps", "gems", "mixed"])
            rag_examples = examples
        else:
            rag_examples = retrieve_calibration_examples_lightweight(
                query=rag_query,
                venue_type=venue_type,
                n_per_verdict=2
            )

        if verbose:
            print(f"  RAG examples: {rag_examples['total']} (excluding self: {exclude_from_rag})")

    # Compute metrics from synthetic reviews
    metrics = compute_metrics(reviews_low, reviews_high, venue_type=venue_type)

    # Add proximity signal if applicable
    if proximity_data.get("proximity_score", 0) > 70:
        metrics["signals"].append({
            "signal": "tourist_hotspot_location",
            "severity": "medium",
            "detail": f"Located in high-tourist area (score: {proximity_data['proximity_score']}/100)",
        })

    # Add external signal if negative
    neg_sentiments = sum(1 for s in [
        external_opinions.get("reddit_sentiment"),
        external_opinions.get("tripadvisor_sentiment"),
        external_opinions.get("blog_sentiment")
    ] if s == "negative")

    if neg_sentiments >= 2:
        metrics["signals"].append({
            "signal": "external_negative_reputation",
            "severity": "high",
            "detail": f"Negative sentiment on external platforms",
        })

    # Build prompt
    prompt = _build_prompt(place, metrics, external_opinions, proximity_data)

    # Add RAG examples if available
    if rag_examples and rag_examples["total"] > 0:
        from src.rag.retriever_lightweight import format_examples_for_prompt
        rag_section = format_examples_for_prompt(rag_examples)
        full_prompt = f"{SYSTEM_PROMPT}\n\n{rag_section}\n\n{prompt}"
    else:
        full_prompt = f"{SYSTEM_PROMPT}\n\n{prompt}"

    # Call Gemini
    generation_config = {
        "maxOutputTokens": 4096,
        "responseMimeType": "application/json",
        "responseSchema": RESPONSE_SCHEMA
    }
    if temperature is not None:
        generation_config["temperature"] = temperature

    try:
        response = httpx.post(
            GEMINI_API_URL,
            params={"key": GOOGLE_API_KEY},
            json={
                "contents": [{"parts": [{"text": full_prompt}]}],
                "generationConfig": generation_config
            },
            timeout=60.0
        )
        response.raise_for_status()
        result = response.json()

        response_text = result["candidates"][0]["content"]["parts"][0]["text"]
        analysis = json.loads(response_text)

    except Exception as e:
        return {
            "error": str(e),
            "ground_truth": {
                "score": entry["tourist_trap_score"],
                "verdict": entry["verdict"],
            }
        }

    # Add metadata
    analysis["meta"] = {
        "entry_id": entry["id"],
        "place_name": entry["name"],
        "location": entry["location"],
        "venue_type": venue_type,
        "rag_enabled": use_rag,
        "exclude_from_rag": exclude_from_rag,
    }
    analysis["ground_truth"] = {
        "score": entry["tourist_trap_score"],
        "verdict": entry["verdict"],
    }
    analysis["computed_metrics"] = metrics["summary"]
    analysis["signals"] = metrics["signals"]

    return analysis


def _build_prompt(place: dict, metrics: dict, external_opinions: dict, proximity_data: dict) -> str:
    """Build the analysis prompt from mock data."""
    prompt = f"""## VENUE INFORMATION
Name: {place['name']}
Address: {place['address']}
Overall Rating: {place['rating']} stars
Total Reviews: {place['review_count']}
Price Level: {place['price_level'] or 'Not specified'}
Type: {place.get('type', ['restaurant'])}

## COMPUTED SIGNALS

### Summary Metrics
- Low-rating reviews analyzed: {metrics['summary']['total_low_rating_reviews']}
- High-rating reviews analyzed: {metrics['summary']['total_high_rating_reviews']}
- Average credibility of negative reviewers: {metrics['summary']['avg_credibility_low_rating']}/100
- Average credibility of positive reviewers: {metrics['summary']['avg_credibility_high_rating']}/100
- Credibility gap: {metrics['summary']['credibility_gap']:+.1f} (positive gap = trap signal, negative gap = authenticity signal)
- Local Guides in negative reviews: {metrics['summary']['local_guides_in_negative']}
- Local Guides in positive reviews: {metrics['summary']['local_guides_in_positive']}
- Reviews explicitly warning "tourist trap": {metrics['summary']['trap_warning_count']}
- Reviews accusing fake/bought reviews: {metrics['summary']['manipulation_accusation_count']}
- Reviews with quality complaints: {metrics['summary']['quality_complaint_count']}
- Average specificity of positive reviews: {metrics['summary'].get('avg_specificity_positive', 'N/A')}/100

### Detected Signals
{json.dumps(metrics['signals'], indent=2) if metrics['signals'] else "No significant signals detected"}

## EXTERNAL SIGNALS

### Location Analysis
- Tourist Hotspot: {'Yes' if proximity_data.get('is_tourist_hotspot') else 'No'}
- Proximity Score: {proximity_data.get('proximity_score', 'N/A')}/100
- Assessment: {proximity_data.get('reasoning', 'N/A')}

### External Opinions
- Reddit Sentiment: {external_opinions.get('reddit_sentiment', 'none')}
- TripAdvisor Sentiment: {external_opinions.get('tripadvisor_sentiment', 'none')}
- Blog Sentiment: {external_opinions.get('blog_sentiment', 'none')}
- External Warnings: {external_opinions.get('external_warnings', 0)}
- External Recommendations: {external_opinions.get('external_recommendations', 0)}
- Summary: {external_opinions.get('summary', 'No data')}

## MOST CREDIBLE NEGATIVE REVIEWS

"""
    for i, review in enumerate(metrics.get('credible_negative_reviews', [])[:5], 1):
        prompt += f"""
### Review {i}
- Rating: {review['rating']}/5
- Reviewer credibility: {review['credibility_score']}/100
- Local Guide: {'Yes' if review['is_local_guide'] else 'No'}
- Trap keywords found: {review['trap_keywords'] or 'None'}
- Text: "{review['text'][:300]}{'...' if len(review['text'] or '') > 300 else ''}"
"""

    prompt += """
## MOST CREDIBLE POSITIVE REVIEWS

"""
    for i, review in enumerate(metrics.get('credible_positive_reviews', [])[:3], 1):
        text = review.get('text') or ''
        prompt += f"""
### Positive Review {i}
- Rating: {review['rating']}/5
- Reviewer credibility: {review['credibility_score']}/100
- Specificity score: {review.get('specificity_score', 'N/A')}/100
- Local Guide: {'Yes' if review['is_local_guide'] else 'No'}
- Text: "{text[:250]}{'...' if len(text) > 250 else ''}"
"""

    prompt += "\n\nBased on these metrics and reviews, provide your analysis."
    return prompt


def run_evaluation(
    n_samples: Optional[int] = None,
    categories: Optional[list[str]] = None,
    use_rag: bool = True,
    verbose: bool = True,
) -> dict:
    """
    Run evaluation on RAG entries.

    Args:
        n_samples: Number of samples per category (None = all)
        categories: List of categories to test (None = all)
        use_rag: Whether to use RAG calibration
        verbose: Print progress

    Returns:
        Evaluation results dict
    """
    from src.test_harness import evaluate_prediction, verdict_to_category, score_to_category

    entries = load_rag_database()

    # Filter by category if specified
    if categories:
        entries = [e for e in entries if e["verdict"] in categories]

    # Sample if specified
    if n_samples:
        import random
        # Stratified sampling
        by_verdict = {}
        for e in entries:
            v = e["verdict"]
            if v not in by_verdict:
                by_verdict[v] = []
            by_verdict[v].append(e)

        entries = []
        for v, items in by_verdict.items():
            random.shuffle(items)
            entries.extend(items[:n_samples])

    results = []
    errors = []

    for i, entry in enumerate(entries):
        if verbose:
            print(f"[{i+1}/{len(entries)}] {entry['name']} (GT: {entry['verdict']}, {entry['tourist_trap_score']})")

        analysis = analyze_synthetic(entry, exclude_from_rag=True, use_rag=use_rag)

        if "error" in analysis:
            errors.append({"entry": entry["id"], "error": analysis["error"]})
            if verbose:
                print(f"  ERROR: {analysis['error']}")
            continue

        predicted = analysis.get("tourist_trap_score", 50)
        gt_score = entry["tourist_trap_score"]
        gt_verdict = entry["verdict"]

        eval_result = evaluate_prediction(predicted, gt_score, gt_verdict)
        eval_result["entry_id"] = entry["id"]
        eval_result["name"] = entry["name"]
        eval_result["predicted_verdict"] = analysis.get("classification", "unknown")

        results.append(eval_result)

        if verbose:
            match_str = "✓" if eval_result["category_match"] else "✗"
            print(f"  Predicted: {predicted} ({eval_result['predicted_category']}) vs GT: {gt_score} ({eval_result['true_category']}) {match_str}")

    # Compute aggregate metrics
    if results:
        n = len(results)
        category_matches = sum(1 for r in results if r["category_match"])
        within_15 = sum(1 for r in results if r["within_15"])
        within_20 = sum(1 for r in results if r["within_20"])
        avg_diff = sum(r["score_diff"] for r in results) / n

        # Per-category accuracy
        by_category = {}
        for r in results:
            cat = r["true_category"]
            if cat not in by_category:
                by_category[cat] = {"total": 0, "correct": 0}
            by_category[cat]["total"] += 1
            if r["category_match"]:
                by_category[cat]["correct"] += 1

        summary = {
            "total_tested": n,
            "errors": len(errors),
            "category_accuracy": category_matches / n,
            "within_15_accuracy": within_15 / n,
            "within_20_accuracy": within_20 / n,
            "avg_score_diff": avg_diff,
            "per_category": {
                cat: data["correct"] / data["total"]
                for cat, data in by_category.items()
            }
        }
    else:
        summary = {"total_tested": 0, "errors": len(errors)}

    return {
        "summary": summary,
        "results": results,
        "errors": errors,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run synthetic evaluation")
    parser.add_argument("--samples", "-n", type=int, default=3, help="Samples per category")
    parser.add_argument("--no-rag", action="store_true", help="Disable RAG")
    parser.add_argument("--category", "-c", choices=["tourist_trap", "local_gem", "mixed"], help="Test single category")

    args = parser.parse_args()

    categories = [args.category] if args.category else None

    print("=" * 60)
    print("TrapCheck Synthetic Evaluation")
    print("=" * 60)
    print(f"Samples per category: {args.samples}")
    print(f"RAG enabled: {not args.no_rag}")
    print(f"Categories: {categories or 'all'}")
    print("=" * 60)
    print()

    results = run_evaluation(
        n_samples=args.samples,
        categories=categories,
        use_rag=not args.no_rag,
        verbose=True,
    )

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    summary = results["summary"]
    print(f"Total tested: {summary['total_tested']}")
    print(f"Errors: {summary.get('errors', 0)}")
    if summary["total_tested"] > 0:
        print(f"Category accuracy: {summary['category_accuracy']:.1%}")
        print(f"Within ±15 points: {summary['within_15_accuracy']:.1%}")
        print(f"Within ±20 points: {summary['within_20_accuracy']:.1%}")
        print(f"Avg score diff: {summary['avg_score_diff']:.1f}")
        print()
        print("Per-category accuracy:")
        for cat, acc in summary.get("per_category", {}).items():
            print(f"  {cat}: {acc:.1%}")
