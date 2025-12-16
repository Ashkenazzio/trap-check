#!/usr/bin/env python3
"""
Evaluation Framework v2 for TrapCheck

Uses RAG database as ground truth for comprehensive evaluation.
Tests against 30 stratified venues (10 per verdict) with synthetic data.

Usage:
    python scripts/evaluation_v2.py --name baseline
    python scripts/evaluation_v2.py --name temp_0.0 --temperature 0.0
    python scripts/evaluation_v2.py --name rag_keyword --rag --rag-mode keyword
    python scripts/evaluation_v2.py --name rag_vector --rag --rag-mode vector
"""

import argparse
import json
import random
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer_synthetic import analyze_synthetic
from src.test_harness import (
    load_rag_database,
    evaluate_prediction,
    verdict_to_category,
    score_to_category,
)
from src.config import validate_config


@dataclass
class RunResult:
    """Result from a single analysis run."""
    # Core results
    score: int = -1
    classification: str = ""
    confidence: str = ""
    verdict: str = ""

    # Ground truth
    ground_truth_score: int = 0
    ground_truth_verdict: str = ""

    # Evaluation metrics
    score_diff: int = 0
    category_match: bool = False
    within_15: bool = False
    within_20: bool = False

    # Quality metrics
    reasoning_length: int = 0
    key_concerns_count: int = 0
    mitigating_factors_count: int = 0

    # Performance
    latency_seconds: float = 0.0

    # Pre-computed signals
    signals_detected: list = field(default_factory=list)
    signals_count: int = 0

    # Error tracking
    error: Optional[str] = None


@dataclass
class VenueResult:
    """Results for a single venue across multiple runs."""
    entry_id: str
    name: str
    location: str
    category: str
    ground_truth_score: int
    ground_truth_verdict: str

    # Runs
    runs: list = field(default_factory=list)
    valid_runs: int = 0
    failed_runs: int = 0

    # Aggregated scores
    scores: list = field(default_factory=list)
    mean_score: float = 0.0
    stdev_score: float = 0.0
    min_score: int = 0
    max_score: int = 0

    # Accuracy
    mean_score_diff: float = 0.0
    category_accuracy: float = 0.0
    within_15_rate: float = 0.0
    within_20_rate: float = 0.0

    # Performance
    avg_latency: float = 0.0


@dataclass
class ExperimentConfig:
    """Configuration for an experiment."""
    name: str
    samples_per_category: int = 10
    runs_per_venue: int = 3
    temperature: Optional[float] = None
    use_rag: bool = False
    rag_mode: str = "keyword"
    delay_seconds: float = 2.0
    seed: int = 42


@dataclass
class ExperimentResults:
    """Full experiment results."""
    config: dict
    timestamp: str
    venue_results: list
    summary: dict = field(default_factory=dict)


def stratified_sample(entries: list, n_per_category: int, seed: int = 42) -> list:
    """
    Sample n entries from each verdict category.

    Returns list of entries with exactly n from each of:
    - tourist_trap
    - local_gem
    - mixed
    """
    random.seed(seed)

    by_verdict = {"tourist_trap": [], "local_gem": [], "mixed": []}
    for entry in entries:
        verdict = entry.get("verdict", "mixed")
        if verdict in by_verdict:
            by_verdict[verdict].append(entry)

    sampled = []
    for verdict, items in by_verdict.items():
        if len(items) < n_per_category:
            print(f"Warning: Only {len(items)} entries for {verdict}, requested {n_per_category}")
            sampled.extend(items)
        else:
            sampled.extend(random.sample(items, n_per_category))

    random.shuffle(sampled)
    return sampled


def run_single_analysis(
    entry: dict,
    run_number: int,
    config: ExperimentConfig,
) -> RunResult:
    """Run a single analysis and return results."""
    print(f"    Run {run_number}: ", end="", flush=True)

    result = RunResult(
        ground_truth_score=entry["tourist_trap_score"],
        ground_truth_verdict=entry["verdict"],
    )

    try:
        analysis = analyze_synthetic(
            entry,
            exclude_from_rag=True,
            use_rag=config.use_rag,
            temperature=config.temperature,
        )

        if "error" in analysis:
            print(f"ERROR - {str(analysis['error'])[:50]}")
            result.error = str(analysis["error"])
            result.latency_seconds = analysis.get("latency_seconds", 0)
            return result

        # Core results
        result.score = analysis.get("tourist_trap_score", -1)
        result.classification = analysis.get("classification", "unknown")
        result.confidence = analysis.get("confidence", "unknown")
        result.verdict = analysis.get("verdict", "")
        result.latency_seconds = analysis.get("latency_seconds", 0)

        # Evaluation metrics
        eval_result = evaluate_prediction(
            result.score,
            result.ground_truth_score,
            result.ground_truth_verdict,
        )
        result.score_diff = eval_result["score_diff"]
        result.category_match = eval_result["category_match"]
        result.within_15 = eval_result["within_15"]
        result.within_20 = eval_result["within_20"]

        # Quality metrics
        result.reasoning_length = len(analysis.get("reasoning", ""))
        result.key_concerns_count = len(analysis.get("key_concerns", []))
        result.mitigating_factors_count = len(analysis.get("mitigating_factors", []))

        # Signals
        signals = analysis.get("signals", [])
        result.signals_detected = [s.get("signal", "") for s in signals]
        result.signals_count = len(signals)

        # Print summary
        match_str = "✓" if result.category_match else "✗"
        print(f"Score={result.score} (GT={result.ground_truth_score}, diff={result.score_diff}) "
              f"{match_str} {result.latency_seconds:.1f}s")

    except Exception as e:
        print(f"EXCEPTION - {str(e)[:50]}")
        result.error = str(e)

    return result


def run_venue_evaluation(
    entry: dict,
    config: ExperimentConfig,
) -> VenueResult:
    """Run multiple analyses for a single venue."""
    print(f"\n  {entry['name']} ({entry['location']}) - GT: {entry['verdict']}, {entry['tourist_trap_score']}")

    venue_result = VenueResult(
        entry_id=entry["id"],
        name=entry["name"],
        location=entry["location"],
        category=entry.get("category", "unknown"),
        ground_truth_score=entry["tourist_trap_score"],
        ground_truth_verdict=entry["verdict"],
    )

    runs = []
    for i in range(config.runs_per_venue):
        result = run_single_analysis(entry, i + 1, config)
        runs.append(result)

        if i < config.runs_per_venue - 1:
            time.sleep(config.delay_seconds)

    venue_result.runs = [asdict(r) for r in runs]

    # Aggregate valid runs
    valid_runs = [r for r in runs if r.score >= 0 and not r.error]
    venue_result.valid_runs = len(valid_runs)
    venue_result.failed_runs = len(runs) - len(valid_runs)

    if valid_runs:
        scores = [r.score for r in valid_runs]
        venue_result.scores = scores
        venue_result.mean_score = statistics.mean(scores)
        venue_result.stdev_score = statistics.stdev(scores) if len(scores) > 1 else 0
        venue_result.min_score = min(scores)
        venue_result.max_score = max(scores)

        venue_result.mean_score_diff = statistics.mean(r.score_diff for r in valid_runs)
        venue_result.category_accuracy = sum(1 for r in valid_runs if r.category_match) / len(valid_runs)
        venue_result.within_15_rate = sum(1 for r in valid_runs if r.within_15) / len(valid_runs)
        venue_result.within_20_rate = sum(1 for r in valid_runs if r.within_20) / len(valid_runs)
        venue_result.avg_latency = statistics.mean(r.latency_seconds for r in valid_runs)

    return venue_result


def calculate_summary(venue_results: list[VenueResult]) -> dict:
    """Calculate aggregate summary metrics."""
    successful = [v for v in venue_results if v.valid_runs > 0]

    if not successful:
        return {"status": "ALL_FAILED"}

    # Group by ground truth verdict for per-category metrics
    by_verdict = {}
    for v in successful:
        verdict = v.ground_truth_verdict
        if verdict not in by_verdict:
            by_verdict[verdict] = []
        by_verdict[verdict].append(v)

    summary = {
        "status": "COMPLETE",
        "total_venues": len(venue_results),
        "successful_venues": len(successful),
        "total_runs": sum(v.valid_runs + v.failed_runs for v in venue_results),
        "successful_runs": sum(v.valid_runs for v in successful),
        "failed_runs": sum(v.failed_runs for v in venue_results),

        # Overall accuracy
        "overall_category_accuracy": statistics.mean(v.category_accuracy for v in successful),
        "overall_within_15": statistics.mean(v.within_15_rate for v in successful),
        "overall_within_20": statistics.mean(v.within_20_rate for v in successful),
        "overall_mae": statistics.mean(v.mean_score_diff for v in successful),

        # Consistency
        "avg_stdev": statistics.mean(v.stdev_score for v in successful),
        "avg_score_range": statistics.mean(v.max_score - v.min_score for v in successful) if successful else 0,

        # Performance
        "avg_latency": statistics.mean(v.avg_latency for v in successful),
        "total_time": sum(v.avg_latency * v.valid_runs for v in successful),

        # Per-category breakdown
        "per_category": {},
    }

    for verdict, venues in by_verdict.items():
        summary["per_category"][verdict] = {
            "count": len(venues),
            "category_accuracy": statistics.mean(v.category_accuracy for v in venues),
            "within_15": statistics.mean(v.within_15_rate for v in venues),
            "mae": statistics.mean(v.mean_score_diff for v in venues),
            "avg_predicted_score": statistics.mean(v.mean_score for v in venues),
        }

    return summary


def generate_markdown_report(results: ExperimentResults, output_path: Path) -> str:
    """Generate markdown report."""
    config = results.config
    summary = results.summary

    lines = [
        f"# Experiment: {config['name']}",
        "",
        "## Configuration",
        f"- **Date:** {results.timestamp}",
        f"- **Samples per category:** {config['samples_per_category']}",
        f"- **Runs per venue:** {config['runs_per_venue']}",
        f"- **Temperature:** {config['temperature'] if config['temperature'] is not None else 'default'}",
        f"- **RAG Enabled:** {config['use_rag']}",
        f"- **RAG Mode:** {config['rag_mode'] if config['use_rag'] else 'N/A'}",
        f"- **Seed:** {config['seed']}",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Venues Tested | {summary.get('successful_venues', 0)}/{summary.get('total_venues', 0)} |",
        f"| Total Runs | {summary.get('successful_runs', 0)}/{summary.get('total_runs', 0)} |",
        f"| Category Accuracy | {summary.get('overall_category_accuracy', 0)*100:.1f}% |",
        f"| Within ±15 pts | {summary.get('overall_within_15', 0)*100:.1f}% |",
        f"| Within ±20 pts | {summary.get('overall_within_20', 0)*100:.1f}% |",
        f"| Mean Absolute Error | {summary.get('overall_mae', 0):.1f} |",
        f"| Avg Score StdDev | {summary.get('avg_stdev', 0):.2f} |",
        f"| Avg Latency | {summary.get('avg_latency', 0):.1f}s |",
        "",
        "## Per-Category Results",
        "",
        "| Category | Count | Accuracy | Within ±15 | MAE | Avg Predicted |",
        "|----------|-------|----------|------------|-----|---------------|",
    ]

    for cat, data in summary.get("per_category", {}).items():
        lines.append(
            f"| {cat} | {data['count']} | {data['category_accuracy']*100:.0f}% | "
            f"{data['within_15']*100:.0f}% | {data['mae']:.1f} | {data['avg_predicted_score']:.0f} |"
        )

    lines.extend([
        "",
        "## Individual Venue Results",
        "",
        "| Venue | Location | GT Verdict | GT Score | Predicted | Diff | Match |",
        "|-------|----------|------------|----------|-----------|------|-------|",
    ])

    for v in results.venue_results:
        match = "✓" if v.get("category_accuracy", 0) == 1.0 else "✗"
        lines.append(
            f"| {v['name'][:25]} | {v['location'][:15]} | {v['ground_truth_verdict']} | "
            f"{v['ground_truth_score']} | {v['mean_score']:.0f} | {v['mean_score_diff']:.0f} | {match} |"
        )

    lines.extend([
        "",
        "---",
        f"**Raw Data:** [{output_path.stem}.json]({output_path.stem}.json)",
    ])

    return "\n".join(lines)


def run_experiment(config: ExperimentConfig) -> ExperimentResults:
    """Run a full experiment."""
    print("=" * 70)
    print(f"EXPERIMENT: {config.name}")
    print("=" * 70)
    print(f"Samples per category: {config.samples_per_category}")
    print(f"Runs per venue: {config.runs_per_venue}")
    print(f"Temperature: {config.temperature if config.temperature is not None else 'default'}")
    print(f"RAG: {config.use_rag} ({config.rag_mode})" if config.use_rag else f"RAG: {config.use_rag}")
    print(f"Seed: {config.seed}")

    # Load and sample
    print("\nLoading RAG database...")
    entries = load_rag_database()
    print(f"Total entries: {len(entries)}")

    sampled = stratified_sample(entries, config.samples_per_category, config.seed)
    print(f"Sampled: {len(sampled)} venues")

    total_runs = len(sampled) * config.runs_per_venue
    est_time = total_runs * (config.delay_seconds + 3)
    print(f"Total runs: {total_runs}")
    print(f"Estimated time: {est_time/60:.1f} minutes")
    print("=" * 70)

    # Run evaluations
    venue_results = []
    for i, entry in enumerate(sampled):
        print(f"\n[{i+1}/{len(sampled)}]", end="")
        result = run_venue_evaluation(entry, config)
        venue_results.append(result)

    # Calculate summary
    summary = calculate_summary(venue_results)

    # Build results
    results = ExperimentResults(
        config=asdict(config),
        timestamp=datetime.now().isoformat(),
        venue_results=[asdict(v) for v in venue_results],
        summary=summary,
    )

    # Print summary
    print("\n" + "=" * 70)
    print("EXPERIMENT SUMMARY")
    print("=" * 70)
    print(f"Status: {summary.get('status', 'UNKNOWN')}")
    print(f"Venues: {summary.get('successful_venues', 0)}/{summary.get('total_venues', 0)}")
    print(f"Runs: {summary.get('successful_runs', 0)}/{summary.get('total_runs', 0)}")
    print(f"\nAccuracy:")
    print(f"  Category Accuracy: {summary.get('overall_category_accuracy', 0)*100:.1f}%")
    print(f"  Within ±15 pts: {summary.get('overall_within_15', 0)*100:.1f}%")
    print(f"  Within ±20 pts: {summary.get('overall_within_20', 0)*100:.1f}%")
    print(f"  MAE: {summary.get('overall_mae', 0):.1f}")
    print(f"\nConsistency:")
    print(f"  Avg StdDev: {summary.get('avg_stdev', 0):.2f}")
    print(f"\nPer-category:")
    for cat, data in summary.get("per_category", {}).items():
        print(f"  {cat}: {data['category_accuracy']*100:.0f}% accuracy, MAE={data['mae']:.1f}")
    print(f"\nPerformance:")
    print(f"  Avg Latency: {summary.get('avg_latency', 0):.1f}s")
    print(f"  Total Time: {summary.get('total_time', 0):.1f}s")

    return results


def main():
    parser = argparse.ArgumentParser(description="TrapCheck Evaluation v2")
    parser.add_argument("--name", type=str, required=True, help="Experiment name")
    parser.add_argument("--samples", type=int, default=10, help="Samples per category (default: 10)")
    parser.add_argument("--runs", type=int, default=3, help="Runs per venue (default: 3)")
    parser.add_argument("--temperature", type=float, default=None, help="Gemini temperature")
    parser.add_argument("--rag", action="store_true", help="Enable RAG")
    parser.add_argument("--rag-mode", type=str, default="keyword", choices=["vector", "keyword"])
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between runs (default: 2s)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--output-dir", type=str, default="docs/experiments/v2")
    args = parser.parse_args()

    # Validate config
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Create config
    config = ExperimentConfig(
        name=args.name,
        samples_per_category=args.samples,
        runs_per_venue=args.runs,
        temperature=args.temperature,
        use_rag=args.rag,
        rag_mode=args.rag_mode,
        delay_seconds=args.delay,
        seed=args.seed,
    )

    # Run experiment
    results = run_experiment(config)

    # Save results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON
    json_path = output_dir / f"{args.name}.json"
    with open(json_path, "w") as f:
        json.dump(asdict(results), f, indent=2, default=str)
    print(f"\n📄 JSON saved to: {json_path}")

    # Save Markdown
    md_path = output_dir / f"{args.name}.md"
    md_content = generate_markdown_report(results, md_path)
    with open(md_path, "w") as f:
        f.write(md_content)
    print(f"📝 Report saved to: {md_path}")


if __name__ == "__main__":
    main()
