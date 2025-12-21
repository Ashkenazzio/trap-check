#!/usr/bin/env python3
"""
TrapCheck - Tourist Trap Detector Web UI
"""
import gradio as gr
from src.config import validate_config
from src.analyzer import analyze_venue

# Custom CSS for styling (works with both light and dark themes)
CUSTOM_CSS = """
/* Main container */
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}

/* Theme toggle button */
.theme-toggle {
    position: absolute !important;
    top: 12px !important;
    right: 12px !important;
    min-width: 40px !important;
    width: 40px !important;
    height: 40px !important;
    padding: 0 !important;
    border-radius: 50% !important;
    font-size: 1.2em !important;
    cursor: pointer !important;
    z-index: 1000 !important;
}

/* Header styling */
.header-container {
    text-align: center;
    padding: 12px 0;
    margin-bottom: 12px;
    border-bottom: 1px solid var(--border-color-primary);
    position: relative;
}

.logo-title {
    font-size: 2.5em;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
}

.logo-emoji {
    font-size: 1em;
    -webkit-text-fill-color: initial;
}

.logo-text {
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.tagline {
    color: var(--body-text-color-subdued) !important;
    font-size: 1.1em;
    margin-top: 8px;
}

/* Card styling */
.result-card {
    background: var(--background-fill-secondary) !important;
    border: 1px solid var(--border-color-primary) !important;
    border-radius: 12px !important;
    padding: 20px !important;
}

/* Button styling */
.primary-btn {
    background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
    border: none !important;
    font-weight: 600 !important;
}

.primary-btn:hover {
    opacity: 0.9 !important;
}

/* Hide Gradio's progress indicators */
.progress-bar,
.progress-text,
.eta-bar,
.progress-level,
.progress-level-inner,
.meta-text,
.meta-text-center {
    display: none !important;
}

/* Loading spinner animation */
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--border-color-primary);
    border-top: 4px solid #f97316;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px auto;
}

/* Tab styling */
.tabs {
    border: 1px solid var(--border-color-primary) !important;
    border-radius: 8px !important;
    overflow: hidden;
}

button.tab-nav {
    background: var(--background-fill-secondary) !important;
    border: none !important;
    color: var(--body-text-color-subdued) !important;
    padding: 8px 12px !important;
    font-size: 0.9em !important;
}

button.tab-nav.selected {
    background: var(--background-fill-primary) !important;
    color: #f97316 !important;
}

/* Analysis tab content */
.prose, .markdown-body, .md, .analysis-content {
    max-width: 100% !important;
    overflow-wrap: break-word !important;
    word-wrap: break-word !important;
    color: var(--body-text-color) !important;
    line-height: 1.6 !important;
}

.analysis-content p {
    margin-bottom: 8px !important;
}

/* Examples table */
.examples-table {
    border: 1px solid var(--border-color-primary) !important;
    border-radius: 8px !important;
}

/* ===========================================
   Theme-aware semantic colors
   Light mode: lighter backgrounds, darker text
   Dark mode: darker backgrounds, lighter text
   =========================================== */

/* Danger/Red - for warnings, errors, negative metrics */
.metric-danger {
    background: #fef2f2 !important;
    border: 1px solid #fecaca !important;
}
.metric-danger-value {
    color: #dc2626 !important;
}
.alert-danger {
    background: #fef2f2 !important;
    border: 1px solid #fecaca !important;
}
.alert-danger-title {
    color: #dc2626 !important;
}
.severity-high {
    background: #fef2f2 !important;
    border-left: 4px solid #dc2626 !important;
}
.severity-high-label {
    color: #dc2626 !important;
}

/* Warning/Orange - medium severity */
.severity-medium {
    background: #fff7ed !important;
    border-left: 4px solid #ea580c !important;
}
.severity-medium-label {
    color: #ea580c !important;
}

/* Low severity/Yellow */
.severity-low {
    background: #fefce8 !important;
    border-left: 4px solid #ca8a04 !important;
}
.severity-low-label {
    color: #ca8a04 !important;
}

/* Success/Green - for positive metrics */
.metric-success {
    background: #f0fdf4 !important;
    border: 1px solid #bbf7d0 !important;
}
.metric-success-value {
    color: #16a34a !important;
}
.alert-success-item {
    background: #f0fdf4 !important;
}
.alert-success-icon {
    color: #16a34a !important;
}

/* Neutral - for zero/empty values */
.metric-neutral {
    background: var(--background-fill-secondary) !important;
    border: 1px solid var(--border-color-primary) !important;
}
.metric-neutral-value {
    color: var(--body-text-color-subdued) !important;
}

/* Dark mode overrides */
.dark .metric-danger {
    background: #450a0a !important;
    border: 1px solid #7f1d1d !important;
}
.dark .metric-danger-value {
    color: #fca5a5 !important;
}
.dark .alert-danger {
    background: #450a0a !important;
    border: 1px solid #7f1d1d !important;
}
.dark .alert-danger-title {
    color: #fca5a5 !important;
}
.dark .severity-high {
    background: #450a0a !important;
    border-left: 4px solid #ef4444 !important;
}
.dark .severity-high-label {
    color: #ef4444 !important;
}

.dark .severity-medium {
    background: #431407 !important;
    border-left: 4px solid #f97316 !important;
}
.dark .severity-medium-label {
    color: #f97316 !important;
}

.dark .severity-low {
    background: #422006 !important;
    border-left: 4px solid #eab308 !important;
}
.dark .severity-low-label {
    color: #eab308 !important;
}

.dark .metric-success {
    background: #052e16 !important;
    border: 1px solid #166534 !important;
}
.dark .metric-success-value {
    color: #86efac !important;
}
.dark .alert-success-item {
    background: #052e16 !important;
}
.dark .alert-success-icon {
    color: #86efac !important;
}

/* ===========================================
   Score-based colors for verdict/score display
   =========================================== */

/* Danger (80+) - red */
.score-danger .score-value { color: #dc2626 !important; }
.score-danger .score-badge { background: #fef2f2 !important; color: #dc2626 !important; border-color: #dc2626 !important; }
.score-danger.verdict-box { background: #fef2f2 !important; border-left-color: #dc2626 !important; }
.dark .score-danger .score-value { color: #ef4444 !important; text-shadow: 0 0 30px #ef444440; }
.dark .score-danger .score-badge { background: #450a0a !important; color: #ef4444 !important; border-color: #ef4444 !important; }
.dark .score-danger.verdict-box { background: #450a0a !important; border-left-color: #ef4444 !important; }

/* Warning (60-79) - orange */
.score-warning .score-value { color: #ea580c !important; }
.score-warning .score-badge { background: #fff7ed !important; color: #ea580c !important; border-color: #ea580c !important; }
.score-warning.verdict-box { background: #fff7ed !important; border-left-color: #ea580c !important; }
.dark .score-warning .score-value { color: #f97316 !important; text-shadow: 0 0 30px #f9731640; }
.dark .score-warning .score-badge { background: #431407 !important; color: #f97316 !important; border-color: #f97316 !important; }
.dark .score-warning.verdict-box { background: #431407 !important; border-left-color: #f97316 !important; }

/* Caution (40-59) - yellow */
.score-caution .score-value { color: #ca8a04 !important; }
.score-caution .score-badge { background: #fefce8 !important; color: #ca8a04 !important; border-color: #ca8a04 !important; }
.score-caution.verdict-box { background: #fefce8 !important; border-left-color: #ca8a04 !important; }
.dark .score-caution .score-value { color: #eab308 !important; text-shadow: 0 0 30px #eab30840; }
.dark .score-caution .score-badge { background: #422006 !important; color: #eab308 !important; border-color: #eab308 !important; }
.dark .score-caution.verdict-box { background: #422006 !important; border-left-color: #eab308 !important; }

/* OK (20-39) - lime */
.score-ok .score-value { color: #65a30d !important; }
.score-ok .score-badge { background: #f7fee7 !important; color: #65a30d !important; border-color: #65a30d !important; }
.score-ok.verdict-box { background: #f7fee7 !important; border-left-color: #65a30d !important; }
.dark .score-ok .score-value { color: #84cc16 !important; text-shadow: 0 0 30px #84cc1640; }
.dark .score-ok .score-badge { background: #1a2e05 !important; color: #84cc16 !important; border-color: #84cc16 !important; }
.dark .score-ok.verdict-box { background: #1a2e05 !important; border-left-color: #84cc16 !important; }

/* Safe (0-19) - green */
.score-safe .score-value { color: #16a34a !important; }
.score-safe .score-badge { background: #f0fdf4 !important; color: #16a34a !important; border-color: #16a34a !important; }
.score-safe.verdict-box { background: #f0fdf4 !important; border-left-color: #16a34a !important; }
.dark .score-safe .score-value { color: #22c55e !important; text-shadow: 0 0 30px #22c55e40; }
.dark .score-safe .score-badge { background: #052e16 !important; color: #22c55e !important; border-color: #22c55e !important; }
.dark .score-safe.verdict-box { background: #052e16 !important; border-left-color: #22c55e !important; }

/* Fixed height containers to prevent layout shift */
.fixed-header {
    min-height: 100px;
    box-sizing: border-box;
}

.fixed-score {
    min-height: 180px;
    box-sizing: border-box;
}

.fixed-verdict {
    min-height: 60px;
    box-sizing: border-box;
}

.fixed-metrics {
    min-height: 130px;
    box-sizing: border-box;
}

/* Target only the results row to prevent layout flicker */
.results-row {
    flex-wrap: nowrap !important;
}

/* Fixed width left column (sidebar) */
.results-row > .column:first-child {
    flex: 0 0 320px !important;
    width: 320px !important;
    min-width: 320px !important;
    max-width: 320px !important;
}

/* Flexible right column takes remaining space */
.results-row > .column:last-child {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    overflow: hidden;
}

/* Ensure tab content doesn't cause width changes */
.results-row .tabs {
    width: 100%;
}

.results-row .tabitem {
    width: 100%;
}

/* Prevent content from expanding container */
.fixed-tab-content {
    min-height: 180px;
    box-sizing: border-box;
    overflow-wrap: break-word;
    word-wrap: break-word;
}
"""

# Empty state placeholders - match final layout exactly with neutral/empty values
# Using CSS variables for theme compatibility
EMPTY_HEADER = """
<div class="fixed-header" style='text-align: center; padding: 16px; background: var(--background-fill-secondary); border-radius: 10px; border: 1px solid var(--border-color-primary);'>
    <h2 style='margin: 0; color: var(--body-text-color-subdued); font-size: 1.3em;'>Venue Name</h2>
    <p style='color: var(--body-text-color-subdued); margin: 6px 0 0 0; font-size: 0.85em;'>Enter a venue to analyze</p>
    <div style='margin-top: 8px; display: flex; justify-content: center; align-items: center; gap: 8px;'>
        <span style='color: var(--body-text-color-subdued);'>★ —</span>
        <span style='color: var(--border-color-primary);'>•</span>
        <span style='color: var(--body-text-color-subdued); font-size: 0.9em;'>— reviews</span>
    </div>
</div>
"""

EMPTY_SCORE = """
<div class="fixed-score" style='text-align: center; padding: 20px; background: var(--background-fill-secondary); border-radius: 10px; border: 1px solid var(--border-color-primary);'>
    <div style='font-size: 3em; font-weight: 700; color: var(--border-color-primary);'>
        — —
    </div>
    <div style='font-size: 0.85em; color: var(--body-text-color-subdued); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.1em;'>
        Tourist Trap Score
    </div>
    <div style='margin-top: 12px;'>
        <span style='padding: 6px 16px; background: var(--background-fill-primary); color: var(--body-text-color-subdued); border-radius: 16px; font-weight: 600; font-size: 0.8em; border: 1px solid var(--border-color-primary);'>
            AWAITING ANALYSIS
        </span>
    </div>
    <div style='color: var(--border-color-primary); margin-top: 8px; font-size: 0.8em;'>
        Confidence: <span style='color: var(--body-text-color-subdued);'>—</span>
    </div>
</div>
"""

EMPTY_VERDICT = """
<div class="fixed-verdict" style='padding: 14px; background: var(--background-fill-secondary); border-radius: 10px; border-left: 4px solid var(--border-color-primary);'>
    <p style='font-size: 1em; margin: 0; font-style: italic; color: var(--body-text-color-subdued); line-height: 1.5;'>
        "Analysis verdict will appear here..."
    </p>
</div>
"""

EMPTY_METRICS = """
<div class="fixed-metrics" style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;'>
    <div style='padding: 10px; background: var(--background-fill-secondary); border-radius: 8px; text-align: center; border: 1px solid var(--border-color-primary);'>
        <div style='font-size: 1.5em; font-weight: 700; color: var(--body-text-color-subdued);'>—</div>
        <div style='font-size: 0.7em; color: var(--body-text-color-subdued); margin-top: 2px;'>Trap Warnings</div>
    </div>
    <div style='padding: 10px; background: var(--background-fill-secondary); border-radius: 8px; text-align: center; border: 1px solid var(--border-color-primary);'>
        <div style='font-size: 1.5em; font-weight: 700; color: var(--body-text-color-subdued);'>—</div>
        <div style='font-size: 0.7em; color: var(--body-text-color-subdued); margin-top: 2px;'>Fake Review Claims</div>
    </div>
    <div style='padding: 10px; background: var(--background-fill-secondary); border-radius: 8px; text-align: center; border: 1px solid var(--border-color-primary);'>
        <div style='font-size: 1.5em; font-weight: 700; color: var(--body-text-color-subdued);'>—</div>
        <div style='font-size: 0.7em; color: var(--body-text-color-subdued); margin-top: 2px;'>Local Guides Warning</div>
    </div>
    <div style='padding: 10px; background: var(--background-fill-secondary); border-radius: 8px; text-align: center; border: 1px solid var(--border-color-primary);'>
        <div style='font-size: 1.5em; font-weight: 700; color: var(--body-text-color-subdued);'>—</div>
        <div style='font-size: 0.7em; color: var(--body-text-color-subdued); margin-top: 2px;'>Credibility Gap</div>
    </div>
</div>
"""

EMPTY_TAB_CONTENT = """
<div class="fixed-tab-content" style='padding: 16px;'>
    <p style='color: var(--body-text-color-subdued); text-align: center;'>Run an analysis to see results</p>
</div>
"""

# Loading state - shows spinner in header while keeping other areas with empty state
LOADING_HEADER = """
<div class="fixed-header" style='text-align: center; padding: 16px; background: var(--background-fill-secondary); border-radius: 10px; border: 1px solid var(--border-color-primary);'>
    <div class="loading-spinner"></div>
    <div style='color: #f97316; font-size: 1.1em; font-weight: 500;'>Analyzing...</div>
    <div style='color: var(--body-text-color-subdued); margin-top: 4px; font-size: 0.9em;'>Fetching reviews and computing metrics</div>
</div>
"""


def get_score_class(score: int) -> str:
    """Get CSS class based on trap score."""
    if score >= 80:
        return "score-danger"  # red - definite trap
    elif score >= 60:
        return "score-warning"  # orange - likely trap
    elif score >= 40:
        return "score-caution"  # yellow - possibly trap
    elif score >= 20:
        return "score-ok"  # lime - likely ok
    else:
        return "score-safe"  # green - safe


def get_classification_emoji(classification: str) -> str:
    """Get emoji for classification."""
    emojis = {
        "definite_trap": "🚨",
        "likely_trap": "⚠️",
        "possibly_trap": "🤔",
        "unclear": "❓",
        "likely_authentic": "✅",
        "verified_authentic": "💎",
    }
    return emojis.get(classification, "❓")


# Human-friendly signal name mapping
SIGNAL_NAMES = {
    "credibility_inversion": "Credibility Inversion",
    "explicit_trap_warnings": "Explicit Trap Warnings",
    "manipulation_accusations": "Fake Review Accusations",
    "review_clustering": "Suspicious Review Clustering",
    "local_guide_warnings": "Local Guide Warnings",
    "language_credibility_split": "Tourist vs Local Language Split",
    "generic_positive_reviews": "Generic Positive Reviews",
    "tourist_hotspot_location": "Tourist Hotspot Location",
    "external_negative_reputation": "Negative External Reputation",
    "service_food_disparity": "Service vs Food Quality Gap",
}


def format_signals_html(signals: list) -> str:
    """Format detected signals as HTML."""
    if not signals:
        return "<div class='fixed-tab-content'><p style='color: var(--body-text-color-subdued); padding: 16px;'>No significant signals detected</p></div>"

    html = "<div class='fixed-tab-content'>"
    for signal in signals:
        severity = signal.get("severity", "medium")
        # CSS classes for theme-aware colors
        severity_class = f"severity-{severity}"

        signal_key = signal.get('signal', 'Unknown')
        signal_name = SIGNAL_NAMES.get(signal_key, signal_key.replace('_', ' ').title())

        html += f"""
        <div class='{severity_class}' style='margin-bottom: 12px; padding: 14px; border-radius: 8px;'>
            <span class='{severity_class}-label' style='font-weight: 600; font-size: 0.75em; text-transform: uppercase; letter-spacing: 0.05em;'>{severity}</span>
            <div style='color: var(--body-text-color); font-weight: 500; margin-top: 4px;'>{signal_name}</div>
            <div style='color: var(--body-text-color-subdued); font-size: 0.9em; margin-top: 4px;'>{signal.get('detail', '')}</div>
        </div>
        """
    html += "</div>"
    return html


def format_concerns_html(concerns: list) -> str:
    """Format key concerns as HTML."""
    if not concerns:
        return "<div class='fixed-tab-content'><p style='color: var(--body-text-color-subdued); padding: 16px;'>No specific concerns identified</p></div>"

    html = "<div class='fixed-tab-content'>"
    for concern in concerns:
        html += f"""
        <div class='alert-danger' style='margin-bottom: 12px; padding: 14px; border-radius: 8px;'>
            <div class='alert-danger-title' style='font-weight: 600;'>⚠️ {concern.get('concern', 'Unknown')}</div>
            <div style='color: var(--body-text-color); font-size: 0.9em; margin-top: 8px;'>
                <span style='color: var(--body-text-color-subdued);'>Evidence:</span> {concern.get('evidence', 'N/A')[:200]}...
            </div>
        </div>
        """
    html += "</div>"
    return html


def format_positives_html(positives: list) -> str:
    """Format mitigating factors as HTML."""
    if not positives:
        return "<div class='fixed-tab-content'><p style='color: var(--body-text-color-subdued); padding: 16px;'>No mitigating factors identified</p></div>"

    html = "<div class='fixed-tab-content' style='padding: 8px;'>"
    for positive in positives:
        html += f"""
        <div class='alert-success-item' style='display: flex; align-items: flex-start; margin-bottom: 10px; padding: 8px; border-radius: 6px;'>
            <span class='alert-success-icon' style='margin-right: 8px;'>✓</span>
            <span style='color: var(--body-text-color);'>{positive}</span>
        </div>
        """
    html += "</div>"
    return html


def analyze(query: str, location: str):
    """Run analysis and yield loading state then results."""
    if not query.strip():
        # Return empty state placeholders
        yield (
            EMPTY_HEADER,
            EMPTY_SCORE,
            EMPTY_VERDICT,
            EMPTY_METRICS,
            EMPTY_TAB_CONTENT,
            EMPTY_TAB_CONTENT,
            EMPTY_TAB_CONTENT,
            EMPTY_TAB_CONTENT,
        )
        return

    # Show loading state with spinner in header, empty placeholders elsewhere
    yield (
        LOADING_HEADER,
        EMPTY_SCORE,
        EMPTY_VERDICT,
        EMPTY_METRICS,
        EMPTY_TAB_CONTENT,
        EMPTY_TAB_CONTENT,
        EMPTY_TAB_CONTENT,
        EMPTY_TAB_CONTENT,
    )

    try:
        location_clean = location.strip() if location else None
        # Use keyword-based RAG by default for best accuracy with minimal latency
        result = analyze_venue(query.strip(), location_clean, use_rag=True, rag_mode="keyword")
    except Exception as e:
        error_html = f"""
        <div class="fixed-header" style='text-align: center; padding: 30px; background: #7f1d1d; border-radius: 12px; border: 1px solid #991b1b;'>
            <div style='color: #fca5a5; font-size: 1.2em; font-weight: 600;'>⚠️ Error</div>
            <div style='color: var(--body-text-color); margin-top: 8px;'>{str(e)}</div>
        </div>
        """
        yield (error_html, EMPTY_SCORE, EMPTY_VERDICT, EMPTY_METRICS, EMPTY_TAB_CONTENT, EMPTY_TAB_CONTENT, EMPTY_TAB_CONTENT, EMPTY_TAB_CONTENT)
        return

    if "error" in result:
        error_html = f"""
        <div class="fixed-header" style='text-align: center; padding: 30px; background: #7f1d1d; border-radius: 12px; border: 1px solid #991b1b;'>
            <div style='color: #fca5a5; font-size: 1.2em; font-weight: 600;'>⚠️ Error</div>
            <div style='color: var(--body-text-color); margin-top: 8px;'>{result['error']}</div>
        </div>
        """
        yield (error_html, EMPTY_SCORE, EMPTY_VERDICT, EMPTY_METRICS, EMPTY_TAB_CONTENT, EMPTY_TAB_CONTENT, EMPTY_TAB_CONTENT, EMPTY_TAB_CONTENT)
        return

    # Extract data
    score = result.get("tourist_trap_score", 0)
    classification = result.get("classification", "unclear")
    confidence = result.get("confidence", "low")
    verdict = result.get("verdict", "No verdict available")
    recommendation = result.get("recommendation", "No recommendation available")
    reasoning = result.get("reasoning", "No detailed analysis available")

    meta = result.get("meta", {})
    signals = result.get("signals", [])
    concerns = result.get("key_concerns", [])
    positives = result.get("mitigating_factors", [])
    metrics = result.get("computed_metrics", {})

    # Get CSS class for score-based coloring
    score_class = get_score_class(score)
    emoji = get_classification_emoji(classification)

    # Format header with venue info
    review_count = meta.get('place_review_count', 0)
    review_str = f"{review_count:,}" if isinstance(review_count, int) else str(review_count)

    header_html = f"""
    <div class="fixed-header" style='text-align: center; padding: 16px; background: var(--background-fill-secondary); border-radius: 10px; border: 1px solid var(--border-color-primary);'>
        <h2 style='margin: 0; color: var(--body-text-color); font-size: 1.3em;'>{meta.get('place_name', query)}</h2>
        <p style='color: var(--body-text-color-subdued); margin: 6px 0 0 0; font-size: 0.85em;'>{meta.get('place_address', 'Address not available')}</p>
        <div style='margin-top: 8px; display: flex; justify-content: center; align-items: center; gap: 8px;'>
            <span style='color: #fbbf24;'>★ {meta.get('place_rating', 'N/A')}</span>
            <span style='color: var(--border-color-primary);'>•</span>
            <span style='color: var(--body-text-color-subdued); font-size: 0.9em;'>{review_str} reviews</span>
        </div>
    </div>
    """

    # Format score display using CSS classes
    score_html = f"""
    <div class="fixed-score {score_class}" style='text-align: center; padding: 20px; background: var(--background-fill-secondary); border-radius: 10px; border: 1px solid var(--border-color-primary);'>
        <div class="score-value" style='font-size: 3em; font-weight: 700;'>
            {emoji} {score}
        </div>
        <div style='font-size: 0.85em; color: var(--body-text-color-subdued); margin-top: 4px; text-transform: uppercase; letter-spacing: 0.1em;'>
            Tourist Trap Score
        </div>
        <div style='margin-top: 12px;'>
            <span class="score-badge" style='padding: 6px 16px; border-radius: 16px; font-weight: 600; font-size: 0.8em; border: 1px solid;'>
                {classification.replace('_', ' ').upper()}
            </span>
        </div>
        <div style='color: var(--border-color-primary); margin-top: 8px; font-size: 0.8em;'>
            Confidence: <span style='color: var(--body-text-color-subdued);'>{confidence.upper()}</span>
        </div>
    </div>
    """

    # Format verdict quote using CSS class
    verdict_html = f"""
    <div class="fixed-verdict verdict-box {score_class}" style='padding: 14px; border-radius: 10px; border-left: 4px solid;'>
        <p style='font-size: 1em; margin: 0; font-style: italic; color: var(--body-text-color); line-height: 1.5;'>
            "{verdict}"
        </p>
    </div>
    """

    # Format metrics summary - dark theme compatible
    trap_warnings = metrics.get('trap_warning_count', 0)
    fake_claims = metrics.get('manipulation_accusation_count', 0)
    local_guides = metrics.get('local_guides_in_negative', 0)
    cred_gap = metrics.get('credibility_gap', 0)

    def metric_card(value, label, is_negative=True):
        # Use CSS classes for theme-aware colors
        if is_negative and value > 0:
            card_class = "metric-danger"
        elif not is_negative and value > 0:
            card_class = "metric-success"
        else:
            card_class = "metric-neutral"

        return f"""
        <div class='{card_class}' style='padding: 10px; border-radius: 8px; text-align: center;'>
            <div class='{card_class}-value' style='font-size: 1.5em; font-weight: 700;'>{value}</div>
            <div style='font-size: 0.7em; color: var(--body-text-color-subdued); margin-top: 2px;'>{label}</div>
        </div>
        """

    # Credibility gap special handling
    if cred_gap < -5:
        cred_class = "metric-danger"
    elif cred_gap > 5:
        cred_class = "metric-success"
    else:
        cred_class = "metric-neutral"

    metrics_html = f"""
    <div class="fixed-metrics" style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;'>
        {metric_card(trap_warnings, "Trap Warnings")}
        {metric_card(fake_claims, "Fake Review Claims")}
        {metric_card(local_guides, "Local Guides Warning")}
        <div class='{cred_class}' style='padding: 10px; border-radius: 8px; text-align: center;'>
            <div class='{cred_class}-value' style='font-size: 1.5em; font-weight: 700;'>{cred_gap:+.0f}</div>
            <div style='font-size: 0.7em; color: var(--body-text-color-subdued); margin-top: 2px;'>Credibility Gap</div>
        </div>
    </div>
    """

    signals_html = format_signals_html(signals)
    concerns_html = format_concerns_html(concerns)
    positives_html = format_positives_html(positives)

    # Full analysis as HTML
    analysis_html = f"""
    <div class="fixed-tab-content" style='padding: 20px; color: var(--body-text-color); line-height: 1.7;'>
        <div style='font-weight: 600; color: var(--body-text-color); margin-bottom: 12px;'>Recommendation: {recommendation}</div>
        <hr style='border: none; border-top: 1px solid var(--border-color-primary); margin: 16px 0;'>
        <div style='font-size: 0.95em;'>{reasoning}</div>
    </div>
    """

    yield (
        header_html,
        score_html,
        verdict_html,
        metrics_html,
        signals_html,
        concerns_html,
        positives_html,
        analysis_html,
    )


# JavaScript for theme toggle - will be injected via head parameter
# Gradio uses 'dark' class on document.body to toggle dark mode
THEME_JS = """
<script>
// Theme toggle function - Gradio uses 'dark' class on body
window.toggleTheme = function() {
    const body = document.body;
    const isDark = body.classList.contains('dark');

    if (isDark) {
        body.classList.remove('dark');
        localStorage.setItem('trapcheck-theme', 'light');
    } else {
        body.classList.add('dark');
        localStorage.setItem('trapcheck-theme', 'dark');
    }

    // Update button icon
    const btn = document.querySelector('.theme-toggle');
    if (btn) {
        btn.textContent = body.classList.contains('dark') ? '☀️' : '🌙';
    }
};

// Apply saved theme immediately (light is default)
// Run immediately, not on DOMContentLoaded, to prevent flash
(function() {
    const saved = localStorage.getItem('trapcheck-theme');
    if (saved === 'dark') {
        document.body.classList.add('dark');
    } else {
        // Default to light mode - remove dark class immediately
        document.body.classList.remove('dark');
    }
})();

// Update button icon after DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
        const btn = document.querySelector('.theme-toggle');
        if (btn) {
            btn.textContent = document.body.classList.contains('dark') ? '☀️' : '🌙';
        }
    }, 100);
});
</script>
"""

# Build UI with soft theme (supports light/dark mode)
with gr.Blocks(title="TrapCheck", theme=gr.themes.Soft(), head=THEME_JS) as app:
    # Inject CSS and header with theme toggle
    gr.HTML(f"""
    <style>{CUSTOM_CSS}</style>
    <div class="header-container">
        <h1 class="logo-title">
            <span class="logo-emoji">🎯</span>
            <span class="logo-text">TrapCheck</span>
        </h1>
        <p class="tagline">Detect tourist traps before they catch you</p>
        <button class="theme-toggle" onclick="window.toggleTheme()" title="Toggle theme">🌙</button>
    </div>
    """)

    # Input row
    with gr.Row():
        with gr.Column(scale=3):
            query_input = gr.Textbox(
                label="Restaurant Name",
                placeholder="e.g., Ristorante Luigi, Pizzeria Da Michele...",
                lines=1,
            )
        with gr.Column(scale=2):
            location_input = gr.Textbox(
                label="City/Location",
                placeholder="e.g., Rome, Naples, New York...",
                lines=1,
            )
        with gr.Column(scale=1, min_width=120):
            analyze_btn = gr.Button("🔍 Analyze", variant="primary", size="lg", elem_classes="primary-btn")

    # Results - initialized with empty state placeholders matching final layout
    with gr.Row(elem_classes="results-row"):
        with gr.Column(scale=1, min_width=280):
            header_output = gr.HTML(value=EMPTY_HEADER)
            score_output = gr.HTML(value=EMPTY_SCORE)
            metrics_output = gr.HTML(value=EMPTY_METRICS)

        with gr.Column(scale=2):
            verdict_output = gr.HTML(value=EMPTY_VERDICT)
            with gr.Tabs():
                with gr.Tab("🚨 Signals"):
                    signals_output = gr.HTML(value=EMPTY_TAB_CONTENT)
                with gr.Tab("⚠️ Concerns"):
                    concerns_output = gr.HTML(value=EMPTY_TAB_CONTENT)
                with gr.Tab("✅ Positives"):
                    positives_output = gr.HTML(value=EMPTY_TAB_CONTENT)
                with gr.Tab("📝 Analysis"):
                    analysis_output = gr.HTML(value=EMPTY_TAB_CONTENT, elem_classes="analysis-content")

    # Examples - matches mock data venues for testing without SerpAPI
    gr.Examples(
        examples=[
            ["Pizzeria Da Michele", "Naples"],
            ["Olive Garden Times Square", "New York"],
            ["Carlo Menta", "Rome"],
            ["Katz's Delicatessen", "New York"],
        ],
        inputs=[query_input, location_input],
        label="Test Venues (Mock Data)",
    )

    # Connect handlers
    outputs = [
        header_output,
        score_output,
        verdict_output,
        metrics_output,
        signals_output,
        concerns_output,
        positives_output,
        analysis_output,
    ]

    analyze_btn.click(
        fn=analyze,
        inputs=[query_input, location_input],
        outputs=outputs,
        show_progress="hidden",
    )

    query_input.submit(
        fn=analyze,
        inputs=[query_input, location_input],
        outputs=outputs,
        show_progress="hidden",
    )


if __name__ == "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set up your .env file with API keys.")
        exit(1)

    app.launch(
        share=False,
        favicon_path="static/favicon.svg",
    )
