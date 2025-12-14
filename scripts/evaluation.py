#!/usr/bin/env python3
"""
Comprehensive Evaluation Framework for TrapCheck

Measures accuracy, consistency, quality, and performance metrics for LLM-based analysis.
Supports temperature studies, RAG A/B testing, and experiment comparisons.

Usage:
    python scripts/evaluation.py --name baseline --runs 5
    python scripts/evaluation.py --name temp_0.0 --temperature 0.0 --runs 5 --compare baseline
    python scripts/evaluation.py --name rag_enabled --rag --runs 5 --compare baseline
    python scripts/evaluation.py --name single_venue --venue "da michele" --runs 3
"""

import argparse
import json
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.analyzer import analyze_venue
from src.config import validate_config

# Test venues with ground truth scores for evaluation
TEST_VENUES = [
    {
        "query": "Pizzeria Da Michele",
        "location": "Naples",
        "expected_category": "authentic",
        "expected_score_range": (5, 35),
        "ground_truth_score": 25,
        "rationale": "Historic local favorite, cheap prices, loved by locals",
    },
    {
        "query": "Olive Garden Times Square",
        "location": "New York",
        "expected_category": "trap",
        "expected_score_range": (65, 95),
        "ground_truth_score": 85,
        "rationale": "Chain restaurant in peak tourist hotspot, overpriced",
    },
    {
        "query": "Carlo Menta",
        "location": "Rome",
        "expected_category": "mixed",
        "expected_score_range": (35, 65),
        "ground_truth_score": 50,
        "rationale": "Budget-friendly but low quality, divisive reviews",
    },
    {
        "query": "Katz's Delicatessen",
        "location": "New York",
        "expected_category": "mixed",
        "expected_score_range": (25, 55),
        "ground_truth_score": 35,
        "rationale": "Famous, expensive, but quality justifies - genuinely divisive",
    },
]

# Category to classification mapping
CATEGORY_CLASSIFICATIONS = {
    "authentic": ["verified_authentic", "likely_authentic"],
    "trap": ["definite_trap", "likely_trap", "possibly_trap"],
    "mixed": ["possibly_trap", "unclear", "likely_authentic", "likely_trap"],
}


@dataclass
class RunResult:
    """Result from a single analysis run."""
    # Core results
    score: int = -1
    classification: str = ""
    confidence: str = ""
    verdict: str = ""

    # Quality metrics
    reasoning_length: int = 0
    key_concerns_count: int = 0
    mitigating_factors_count: int = 0
    verdict_length: int = 0

    # Performance
    latency_seconds: float = 0.0

    # Pre-computed signals (should be deterministic)
    signals_detected: list = field(default_factory=list)
    signals_count: int = 0
    computed_metrics: dict = field(default_factory=dict)

    # Error tracking
    error: Optional[str] = None
    rate_limited: bool = False


@dataclass
class VenueMetrics:
    """Aggregated metrics for a venue across multiple runs."""
    venue_name: str
    venue_location: str
    expected_category: str
    expected_range: tuple
    ground_truth: int

    # Raw data
    runs: list = field(default_factory=list)
    valid_runs: int = 0
    failed_runs: int = 0

    # Score statistics
    scores: list = field(default_factory=list)
    mean_score: float = 0.0
    stdev_score: float = 0.0
    min_score: int = 0
    max_score: int = 0
    score_range: int = 0

    # Accuracy metrics
    mae: float = 0.0  # Mean Absolute Error vs ground truth
    in_expected_range: bool = False
    classification_accuracy: float = 0.0  # % matching expected category

    # Consistency metrics
    classifications: list = field(default_factory=list)
    most_common_classification: str = ""
    classification_consistency: float = 0.0
    confidence_distribution: dict = field(default_factory=dict)

    # Quality metrics
    avg_reasoning_length: float = 0.0
    avg_evidence_count: float = 0.0
    avg_verdict_length: float = 0.0

    # Performance metrics
    avg_latency: float = 0.0
    latency_stdev: float = 0.0
    total_latency: float = 0.0

    # Determinism check
    signal_stability: float = 0.0  # % of runs with same signals
    all_signals_detected: dict = field(default_factory=dict)


@dataclass
class ExperimentConfig:
    """Configuration for an experiment run."""
    name: str
    runs_per_venue: int = 5
    temperature: Optional[float] = None
    use_rag: bool = False
    delay_seconds: float = 8.0
    compare_to: Optional[str] = None


@dataclass
class ExperimentResults:
    """Full results from an experiment."""
    config: dict
    timestamp: str
    venue_results: list

    # Aggregate summary
    summary: dict = field(default_factory=dict)

    # Comparison (if --compare used)
    comparison: Optional[dict] = None


def run_single_analysis(
    query: str,
    location: str,
    run_number: int,
    temperature: Optional[float] = None,
    use_rag: bool = False,
) -> RunResult:
    """Run a single analysis and capture comprehensive metrics."""
    print(f"  Run {run_number}: ", end="", flush=True)
    start_time = time.time()

    result = RunResult()

    try:
        analysis = analyze_venue(
            query,
            location,
            temperature=temperature,
            use_rag=use_rag,
        )
        elapsed = time.time() - start_time
        result.latency_seconds = elapsed

        if "error" in analysis:
            error_str = str(analysis["error"])
            print(f"ERROR - {error_str[:60]}")
            result.error = error_str
            if "429" in error_str or "Too Many Requests" in error_str:
                result.rate_limited = True
            return result

        # Core results
        result.score = analysis.get("tourist_trap_score", -1)
        result.classification = analysis.get("classification", "unknown")
        result.confidence = analysis.get("confidence", "unknown")
        result.verdict = analysis.get("verdict", "")

        # Quality metrics
        result.reasoning_length = len(analysis.get("reasoning", ""))
        result.key_concerns_count = len(analysis.get("key_concerns", []))
        result.mitigating_factors_count = len(analysis.get("mitigating_factors", []))
        result.verdict_length = len(result.verdict)

        # Pre-computed signals
        signals = analysis.get("signals", [])
        result.signals_detected = [s.get("signal", "") for s in signals]
        result.signals_count = len(signals)
        result.computed_metrics = analysis.get("computed_metrics", {})

        print(f"Score={result.score}, Class={result.classification}, "
              f"Conf={result.confidence}, Latency={elapsed:.1f}s")

    except Exception as e:
        elapsed = time.time() - start_time
        result.latency_seconds = elapsed
        error_str = str(e)
        print(f"EXCEPTION - {error_str[:60]}")
        result.error = error_str
        if "429" in error_str or "Too Many Requests" in error_str:
            result.rate_limited = True

    return result


def calculate_venue_metrics(venue: dict, runs: list[RunResult]) -> VenueMetrics:
    """Calculate comprehensive metrics for a venue from multiple runs."""
    metrics = VenueMetrics(
        venue_name=venue["query"],
        venue_location=venue["location"],
        expected_category=venue["expected_category"],
        expected_range=venue["expected_score_range"],
        ground_truth=venue["ground_truth_score"],
    )

    # Filter valid runs
    valid_runs = [r for r in runs if r.score >= 0 and not r.error]
    metrics.runs = [asdict(r) for r in runs]
    metrics.valid_runs = len(valid_runs)
    metrics.failed_runs = len(runs) - len(valid_runs)

    if not valid_runs:
        return metrics

    # Score statistics
    scores = [r.score for r in valid_runs]
    metrics.scores = scores
    metrics.mean_score = statistics.mean(scores)
    metrics.stdev_score = statistics.stdev(scores) if len(scores) > 1 else 0
    metrics.min_score = min(scores)
    metrics.max_score = max(scores)
    metrics.score_range = metrics.max_score - metrics.min_score

    # Accuracy metrics
    metrics.mae = statistics.mean(abs(s - metrics.ground_truth) for s in scores)
    low, high = metrics.expected_range
    metrics.in_expected_range = low <= metrics.mean_score <= high

    # Classification accuracy
    expected_classes = CATEGORY_CLASSIFICATIONS.get(metrics.expected_category, [])
    classifications = [r.classification for r in valid_runs]
    correct_classifications = sum(1 for c in classifications if c in expected_classes)
    metrics.classification_accuracy = correct_classifications / len(classifications)

    # Consistency metrics
    metrics.classifications = classifications
    metrics.most_common_classification = max(set(classifications), key=classifications.count)
    metrics.classification_consistency = classifications.count(metrics.most_common_classification) / len(classifications)

    # Confidence distribution
    confidences = [r.confidence for r in valid_runs]
    metrics.confidence_distribution = {c: confidences.count(c) for c in set(confidences)}

    # Quality metrics
    metrics.avg_reasoning_length = statistics.mean(r.reasoning_length for r in valid_runs)
    metrics.avg_evidence_count = statistics.mean(
        r.key_concerns_count + r.mitigating_factors_count for r in valid_runs
    )
    metrics.avg_verdict_length = statistics.mean(r.verdict_length for r in valid_runs)

    # Performance metrics
    latencies = [r.latency_seconds for r in valid_runs]
    metrics.avg_latency = statistics.mean(latencies)
    metrics.latency_stdev = statistics.stdev(latencies) if len(latencies) > 1 else 0
    metrics.total_latency = sum(latencies)

    # Signal stability (determinism check)
    all_signal_sets = [frozenset(r.signals_detected) for r in valid_runs]
    if all_signal_sets:
        most_common_signals = max(set(all_signal_sets), key=all_signal_sets.count)
        metrics.signal_stability = all_signal_sets.count(most_common_signals) / len(all_signal_sets)

        # Track all signals detected across runs
        for r in valid_runs:
            for signal in r.signals_detected:
                metrics.all_signals_detected[signal] = metrics.all_signals_detected.get(signal, 0) + 1

    return metrics


def run_venue_test(
    venue: dict,
    num_runs: int,
    delay: float,
    temperature: Optional[float] = None,
    use_rag: bool = False,
) -> VenueMetrics:
    """Run multiple analyses for a single venue."""
    print(f"\n{'='*70}")
    print(f"Testing: {venue['query']} ({venue['location']})")
    print(f"Expected: {venue['expected_category']} (score {venue['expected_score_range'][0]}-{venue['expected_score_range'][1]})")
    print(f"Ground Truth: {venue['ground_truth_score']}")
    config_str = f"Temperature: {temperature if temperature is not None else 'default'}, RAG: {use_rag}"
    print(f"Config: {config_str}")
    print(f"{'='*70}")

    runs = []
    rate_limited = False

    for i in range(num_runs):
        result = run_single_analysis(
            venue["query"],
            venue["location"],
            i + 1,
            temperature=temperature,
            use_rag=use_rag,
        )
        runs.append(result)

        if result.rate_limited:
            print(f"\n⚠️  RATE LIMITED - stopping test.")
            rate_limited = True
            break

        if i < num_runs - 1:
            print(f"       (waiting {delay}s...)")
            time.sleep(delay)

    # Calculate metrics
    metrics = calculate_venue_metrics(venue, runs)

    # Print summary
    print(f"\n--- Results for {venue['query']} ---")
    if metrics.valid_runs > 0:
        print(f"Scores: {metrics.scores}")
        print(f"Mean: {metrics.mean_score:.1f}, StdDev: {metrics.stdev_score:.2f}, MAE: {metrics.mae:.1f}")
        print(f"Range: {metrics.min_score}-{metrics.max_score} (spread: {metrics.score_range})")
        print(f"Classification: {metrics.most_common_classification} ({metrics.classification_consistency*100:.0f}% consistent)")
        print(f"Classification Accuracy: {metrics.classification_accuracy*100:.0f}%")
        print(f"In Expected Range: {metrics.in_expected_range}")
        print(f"Avg Latency: {metrics.avg_latency:.1f}s")
        print(f"Signal Stability: {metrics.signal_stability*100:.0f}%")
    else:
        print("No valid runs completed.")

    return metrics


def calculate_summary(venue_metrics: list[VenueMetrics]) -> dict:
    """Calculate aggregate summary metrics across all venues."""
    successful = [v for v in venue_metrics if v.valid_runs > 0]

    if not successful:
        return {"status": "ALL_FAILED", "message": "No successful runs"}

    summary = {
        "status": "COMPLETE",
        "venues_tested": len(venue_metrics),
        "venues_successful": len(successful),
        "total_runs": sum(v.valid_runs + v.failed_runs for v in venue_metrics),
        "successful_runs": sum(v.valid_runs for v in successful),
        "failed_runs": sum(v.failed_runs for v in venue_metrics),

        # Accuracy metrics
        "classification_accuracy": statistics.mean(v.classification_accuracy for v in successful),
        "score_calibration": sum(1 for v in successful if v.in_expected_range) / len(successful),
        "avg_mae": statistics.mean(v.mae for v in successful),

        # Consistency metrics
        "avg_stdev": statistics.mean(v.stdev_score for v in successful),
        "avg_score_range": statistics.mean(v.score_range for v in successful),
        "avg_classification_consistency": statistics.mean(v.classification_consistency for v in successful),

        # Quality metrics
        "avg_reasoning_length": statistics.mean(v.avg_reasoning_length for v in successful),
        "avg_evidence_count": statistics.mean(v.avg_evidence_count for v in successful),

        # Performance metrics
        "avg_latency": statistics.mean(v.avg_latency for v in successful),
        "latency_stdev": statistics.mean(v.latency_stdev for v in successful) if len(successful) > 1 else 0,
        "total_time": sum(v.total_latency for v in successful),

        # Determinism check
        "avg_signal_stability": statistics.mean(v.signal_stability for v in successful),
    }

    return summary


def load_experiment(name: str, base_path: str = "docs/experiments") -> Optional[dict]:
    """Load a previous experiment by name."""
    path = Path(base_path) / f"{name}.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def compare_experiments(current: dict, baseline: dict) -> dict:
    """Generate comparison metrics between two experiments."""
    comparison = {
        "baseline_name": baseline["config"]["name"],
        "metrics": {},
        "improved": [],
        "degraded": [],
        "unchanged": [],
    }

    metrics_to_compare = [
        ("avg_stdev", "lower_better", "Score Variance"),
        ("avg_score_range", "lower_better", "Score Range"),
        ("avg_mae", "lower_better", "Mean Absolute Error"),
        ("avg_classification_consistency", "higher_better", "Classification Consistency"),
        ("classification_accuracy", "higher_better", "Classification Accuracy"),
        ("score_calibration", "higher_better", "Score Calibration"),
        ("avg_latency", "lower_better", "Avg Latency"),
        ("avg_signal_stability", "higher_better", "Signal Stability"),
        ("avg_reasoning_length", "higher_better", "Reasoning Length"),
        ("avg_evidence_count", "higher_better", "Evidence Count"),
    ]

    current_summary = current["summary"]
    baseline_summary = baseline["summary"]

    for metric, direction, display_name in metrics_to_compare:
        current_val = current_summary.get(metric)
        baseline_val = baseline_summary.get(metric)

        if current_val is None or baseline_val is None:
            continue

        delta = current_val - baseline_val
        pct_change = (delta / baseline_val * 100) if baseline_val != 0 else 0

        is_improved = (
            (direction == "lower_better" and delta < 0) or
            (direction == "higher_better" and delta > 0)
        )

        comparison["metrics"][metric] = {
            "display_name": display_name,
            "current": round(current_val, 3),
            "baseline": round(baseline_val, 3),
            "delta": round(delta, 3),
            "pct_change": round(pct_change, 1),
            "direction": direction,
            "improved": is_improved,
        }

        if abs(pct_change) < 2:
            comparison["unchanged"].append(display_name)
        elif is_improved:
            comparison["improved"].append(display_name)
        else:
            comparison["degraded"].append(display_name)

    return comparison


def generate_markdown_report(results: ExperimentResults, output_path: Path) -> str:
    """Generate a markdown report from experiment results."""
    lines = [
        f"# Experiment: {results.config['name']}",
        "",
        "## Metadata",
        f"- **Date:** {results.timestamp}",
        f"- **Runs per venue:** {results.config['runs_per_venue']}",
        f"- **Temperature:** {results.config['temperature'] if results.config['temperature'] is not None else 'default'}",
        f"- **RAG Enabled:** {results.config['use_rag']}",
        "",
        "## Summary Metrics",
        "",
        "### Accuracy",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Classification Accuracy | {results.summary.get('classification_accuracy', 0)*100:.1f}% |",
        f"| Score Calibration | {results.summary.get('score_calibration', 0)*100:.1f}% |",
        f"| Mean Absolute Error | {results.summary.get('avg_mae', 0):.2f} |",
        "",
        "### Consistency",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Avg Score StdDev | {results.summary.get('avg_stdev', 0):.2f} |",
        f"| Avg Score Range | {results.summary.get('avg_score_range', 0):.1f} |",
        f"| Classification Consistency | {results.summary.get('avg_classification_consistency', 0)*100:.1f}% |",
        f"| Signal Stability | {results.summary.get('avg_signal_stability', 0)*100:.1f}% |",
        "",
        "### Quality",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Avg Reasoning Length | {results.summary.get('avg_reasoning_length', 0):.0f} chars |",
        f"| Avg Evidence Count | {results.summary.get('avg_evidence_count', 0):.1f} |",
        "",
        "### Performance",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Avg Latency | {results.summary.get('avg_latency', 0):.1f}s |",
        f"| Total Time | {results.summary.get('total_time', 0):.1f}s |",
        "",
        "## Per-Venue Results",
        "",
    ]

    # Per-venue details
    for vm in results.venue_results:
        lines.extend([
            f"### {vm['venue_name']} ({vm['venue_location']})",
            f"- **Expected:** {vm['expected_category']} (score {vm['expected_range'][0]}-{vm['expected_range'][1]})",
            f"- **Ground Truth:** {vm['ground_truth']}",
            f"- **Scores:** {vm['scores']}",
            f"- **Mean:** {vm['mean_score']:.1f}, **StdDev:** {vm['stdev_score']:.2f}, **MAE:** {vm['mae']:.1f}",
            f"- **Classification:** {vm['most_common_classification']} ({vm['classification_consistency']*100:.0f}% consistent)",
            f"- **Classification Accuracy:** {vm['classification_accuracy']*100:.0f}%",
            f"- **In Expected Range:** {'Yes' if vm['in_expected_range'] else 'No'}",
            f"- **Avg Latency:** {vm['avg_latency']:.1f}s",
            f"- **Signal Stability:** {vm['signal_stability']*100:.0f}%",
            "",
        ])

    # Comparison section if available
    if results.comparison:
        comp = results.comparison
        lines.extend([
            "## Comparison with Baseline",
            f"**Baseline:** {comp['baseline_name']}",
            "",
            "| Metric | Baseline | Current | Change | Status |",
            "|--------|----------|---------|--------|--------|",
        ])

        for metric, data in comp["metrics"].items():
            status = "✅" if data["improved"] else "❌" if data["pct_change"] < -2 or data["pct_change"] > 2 else "➖"
            change_str = f"{data['delta']:+.2f} ({data['pct_change']:+.1f}%)"
            lines.append(
                f"| {data['display_name']} | {data['baseline']:.3f} | {data['current']:.3f} | {change_str} | {status} |"
            )

        lines.extend([
            "",
            f"**Improved:** {', '.join(comp['improved']) or 'None'}",
            f"**Degraded:** {', '.join(comp['degraded']) or 'None'}",
            f"**Unchanged:** {', '.join(comp['unchanged']) or 'None'}",
            "",
        ])

    # Decision metrics
    lines.extend([
        "## Decision Metrics",
        "",
        "### Recommendation Score Components",
        f"- **Accuracy Score:** {results.summary.get('classification_accuracy', 0)*100:.1f}%",
        f"- **Consistency Score:** {(1 - results.summary.get('avg_stdev', 10)/20) * results.summary.get('avg_classification_consistency', 0) * 100:.1f}%",
        f"- **Performance Score:** {100 / (1 + results.summary.get('avg_latency', 10)/10):.1f}%",
        "",
    ])

    # Raw data link
    lines.extend([
        "---",
        "",
        f"**Raw Data:** [{output_path.stem}.json]({output_path.stem}.json)",
    ])

    return "\n".join(lines)


def run_experiment(config: ExperimentConfig, venues: list[dict]) -> ExperimentResults:
    """Run a full experiment across all venues."""
    print(f"\n{'='*70}")
    print(f"EXPERIMENT: {config.name}")
    print(f"{'='*70}")
    print(f"Runs per venue: {config.runs_per_venue}")
    print(f"Venues: {len(venues)}")
    print(f"Temperature: {config.temperature if config.temperature is not None else 'default'}")
    print(f"RAG: {config.use_rag}")
    print(f"Delay: {config.delay_seconds}s")

    total_requests = config.runs_per_venue * len(venues)
    estimated_time = total_requests * (config.delay_seconds + 10)
    print(f"Total runs: {total_requests}")
    print(f"Estimated time: {estimated_time/60:.1f} minutes")
    print(f"{'='*70}")

    venue_results = []

    for venue in venues:
        metrics = run_venue_test(
            venue,
            config.runs_per_venue,
            config.delay_seconds,
            temperature=config.temperature,
            use_rag=config.use_rag,
        )
        venue_results.append(metrics)

        # Check for rate limiting
        if any(r.get("rate_limited") for r in metrics.runs):
            print(f"\n🛑 Experiment aborted due to rate limiting.")
            break

    # Calculate summary
    summary = calculate_summary(venue_results)

    # Load baseline for comparison if specified
    comparison = None
    if config.compare_to:
        baseline = load_experiment(config.compare_to)
        if baseline:
            results_dict = {
                "summary": summary,
                "venue_results": [asdict(v) for v in venue_results],
            }
            comparison = compare_experiments(results_dict, baseline)
            print(f"\n📊 Comparison with '{config.compare_to}' generated")
        else:
            print(f"\n⚠️  Baseline '{config.compare_to}' not found, skipping comparison")

    # Build results object
    results = ExperimentResults(
        config=asdict(config),
        timestamp=datetime.now().isoformat(),
        venue_results=[asdict(v) for v in venue_results],
        summary=summary,
        comparison=comparison,
    )

    # Print final summary
    print(f"\n{'='*70}")
    print("EXPERIMENT SUMMARY")
    print(f"{'='*70}")
    print(f"Status: {summary.get('status', 'UNKNOWN')}")
    print(f"Venues: {summary.get('venues_successful', 0)}/{summary.get('venues_tested', 0)}")
    print(f"Runs: {summary.get('successful_runs', 0)}/{summary.get('total_runs', 0)}")
    print(f"\nAccuracy:")
    print(f"  Classification Accuracy: {summary.get('classification_accuracy', 0)*100:.1f}%")
    print(f"  Score Calibration: {summary.get('score_calibration', 0)*100:.1f}%")
    print(f"  Mean Absolute Error: {summary.get('avg_mae', 0):.2f}")
    print(f"\nConsistency:")
    print(f"  Avg StdDev: {summary.get('avg_stdev', 0):.2f}")
    print(f"  Avg Score Range: {summary.get('avg_score_range', 0):.1f}")
    print(f"  Classification Consistency: {summary.get('avg_classification_consistency', 0)*100:.1f}%")
    print(f"  Signal Stability: {summary.get('avg_signal_stability', 0)*100:.1f}%")
    print(f"\nPerformance:")
    print(f"  Avg Latency: {summary.get('avg_latency', 0):.1f}s")
    print(f"  Total Time: {summary.get('total_time', 0):.1f}s")

    if comparison:
        print(f"\nComparison with '{config.compare_to}':")
        print(f"  Improved: {', '.join(comparison['improved']) or 'None'}")
        print(f"  Degraded: {', '.join(comparison['degraded']) or 'None'}")

    return results


def main():
    parser = argparse.ArgumentParser(description="TrapCheck Comprehensive Evaluation")
    parser.add_argument("--name", type=str, required=True, help="Experiment name")
    parser.add_argument("--runs", type=int, default=5, help="Runs per venue (default: 5)")
    parser.add_argument("--temperature", type=float, default=None, help="Gemini temperature (0.0-2.0)")
    parser.add_argument("--rag", action="store_true", help="Enable RAG calibration")
    parser.add_argument("--compare", type=str, default=None, help="Baseline experiment to compare against")
    parser.add_argument("--venue", type=str, default=None, help="Test single venue (partial match)")
    parser.add_argument("--delay", type=float, default=8.0, help="Delay between runs (default: 8s)")
    parser.add_argument("--output-dir", type=str, default="docs/experiments", help="Output directory")
    args = parser.parse_args()

    # Validate config
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Filter venues if specified
    venues = TEST_VENUES
    if args.venue:
        venues = [v for v in TEST_VENUES if args.venue.lower() in v["query"].lower()]
        if not venues:
            print(f"No venues match '{args.venue}'")
            sys.exit(1)

    # Create config
    config = ExperimentConfig(
        name=args.name,
        runs_per_venue=args.runs,
        temperature=args.temperature,
        use_rag=args.rag,
        delay_seconds=args.delay,
        compare_to=args.compare,
    )

    # Run experiment
    results = run_experiment(config, venues)

    # Save results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON
    json_path = output_dir / f"{args.name}.json"
    with open(json_path, "w") as f:
        json.dump(asdict(results), f, indent=2, default=str)
    print(f"\n📄 JSON saved to: {json_path}")

    # Save Markdown report
    md_path = output_dir / f"{args.name}.md"
    md_content = generate_markdown_report(results, md_path)
    with open(md_path, "w") as f:
        f.write(md_content)
    print(f"📝 Report saved to: {md_path}")


if __name__ == "__main__":
    main()
