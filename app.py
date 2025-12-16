#!/usr/bin/env python3
"""
TrapCheck - Tourist Trap Detector Web UI
"""
import gradio as gr
from src.config import validate_config
from src.analyzer import analyze_venue

# Custom CSS for dark theme shadcn-like styling
CUSTOM_CSS = """
/* Main container */
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}

/* Header styling */
.header-container {
    text-align: center;
    padding: 12px 0;
    margin-bottom: 12px;
    border-bottom: 1px solid #333;
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
    color: #9ca3af !important;
    font-size: 1.1em;
    margin-top: 8px;
}

/* Card styling */
.result-card {
    background: #1f2937 !important;
    border: 1px solid #374151 !important;
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
    border: 4px solid #374151;
    border-top: 4px solid #f97316;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px auto;
}

/* Tab styling */
.tabs {
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
    overflow: hidden;
}

button.tab-nav {
    background: #1f2937 !important;
    border: none !important;
    color: #9ca3af !important;
    padding: 8px 12px !important;
    font-size: 0.9em !important;
}

button.tab-nav.selected {
    background: #374151 !important;
    color: #f97316 !important;
}

/* Analysis tab content */
.prose, .markdown-body, .md, .analysis-content {
    max-width: 100% !important;
    overflow-wrap: break-word !important;
    word-wrap: break-word !important;
    color: #d1d5db !important;
    line-height: 1.6 !important;
}

.analysis-content p {
    margin-bottom: 8px !important;
}

/* Examples table */
.examples-table {
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
}

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
EMPTY_HEADER = """
<div class="fixed-header" style='text-align: center; padding: 16px; background: #1f2937; border-radius: 10px; border: 1px solid #374151;'>
    <h2 style='margin: 0; color: #6b7280; font-size: 1.3em;'>Venue Name</h2>
    <p style='color: #4b5563; margin: 6px 0 0 0; font-size: 0.85em;'>Enter a venue to analyze</p>
    <div style='margin-top: 8px; display: flex; justify-content: center; align-items: center; gap: 8px;'>
        <span style='color: #4b5563;'>★ —</span>
        <span style='color: #374151;'>•</span>
        <span style='color: #4b5563; font-size: 0.9em;'>— reviews</span>
    </div>
</div>
"""

EMPTY_SCORE = """
<div class="fixed-score" style='text-align: center; padding: 20px; background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border-radius: 10px; border: 1px solid #374151;'>
    <div style='font-size: 3em; font-weight: 700; color: #374151;'>
        — —
    </div>
    <div style='font-size: 0.85em; color: #4b5563; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.1em;'>
        Tourist Trap Score
    </div>
    <div style='margin-top: 12px;'>
        <span style='padding: 6px 16px; background: #1f2937; color: #4b5563; border-radius: 16px; font-weight: 600; font-size: 0.8em; border: 1px solid #374151;'>
            AWAITING ANALYSIS
        </span>
    </div>
    <div style='color: #374151; margin-top: 8px; font-size: 0.8em;'>
        Confidence: <span style='color: #4b5563;'>—</span>
    </div>
</div>
"""

EMPTY_VERDICT = """
<div class="fixed-verdict" style='padding: 14px; background: #1f2937; border-radius: 10px; border-left: 4px solid #374151;'>
    <p style='font-size: 1em; margin: 0; font-style: italic; color: #4b5563; line-height: 1.5;'>
        "Analysis verdict will appear here..."
    </p>
</div>
"""

EMPTY_METRICS = """
<div class="fixed-metrics" style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;'>
    <div style='padding: 10px; background: #1f2937; border-radius: 8px; text-align: center; border: 1px solid #374151;'>
        <div style='font-size: 1.5em; font-weight: 700; color: #4b5563;'>—</div>
        <div style='font-size: 0.7em; color: #4b5563; margin-top: 2px;'>Trap Warnings</div>
    </div>
    <div style='padding: 10px; background: #1f2937; border-radius: 8px; text-align: center; border: 1px solid #374151;'>
        <div style='font-size: 1.5em; font-weight: 700; color: #4b5563;'>—</div>
        <div style='font-size: 0.7em; color: #4b5563; margin-top: 2px;'>Fake Review Claims</div>
    </div>
    <div style='padding: 10px; background: #1f2937; border-radius: 8px; text-align: center; border: 1px solid #374151;'>
        <div style='font-size: 1.5em; font-weight: 700; color: #4b5563;'>—</div>
        <div style='font-size: 0.7em; color: #4b5563; margin-top: 2px;'>Local Guides Warning</div>
    </div>
    <div style='padding: 10px; background: #1f2937; border-radius: 8px; text-align: center; border: 1px solid #374151;'>
        <div style='font-size: 1.5em; font-weight: 700; color: #4b5563;'>—</div>
        <div style='font-size: 0.7em; color: #4b5563; margin-top: 2px;'>Credibility Gap</div>
    </div>
</div>
"""

EMPTY_TAB_CONTENT = """
<div class="fixed-tab-content" style='padding: 16px;'>
    <p style='color: #4b5563; text-align: center;'>Run an analysis to see results</p>
</div>
"""

# Loading state - shows spinner in header while keeping other areas with empty state
LOADING_HEADER = """
<div class="fixed-header" style='text-align: center; padding: 16px; background: #1f2937; border-radius: 10px; border: 1px solid #374151;'>
    <div class="loading-spinner"></div>
    <div style='color: #f97316; font-size: 1.1em; font-weight: 500;'>Analyzing...</div>
    <div style='color: #9ca3af; margin-top: 4px; font-size: 0.9em;'>Fetching reviews and computing metrics</div>
</div>
"""


def get_score_color(score: int) -> str:
    """Get color based on trap score."""
    if score >= 80:
        return "#ef4444"  # red-500
    elif score >= 60:
        return "#f97316"  # orange-500
    elif score >= 40:
        return "#eab308"  # yellow-500
    elif score >= 20:
        return "#84cc16"  # lime-500
    else:
        return "#22c55e"  # green-500


def get_score_bg(score: int) -> str:
    """Get background color based on trap score (darker variant)."""
    if score >= 80:
        return "#7f1d1d"  # red-900
    elif score >= 60:
        return "#7c2d12"  # orange-900
    elif score >= 40:
        return "#713f12"  # yellow-900
    elif score >= 20:
        return "#365314"  # lime-900
    else:
        return "#14532d"  # green-900


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
        return "<div class='fixed-tab-content'><p style='color: #9ca3af; padding: 16px;'>No significant signals detected</p></div>"

    html = "<div class='fixed-tab-content'>"
    for signal in signals:
        severity = signal.get("severity", "medium")
        colors = {
            "high": ("#ef4444", "#7f1d1d", "#fca5a5"),
            "medium": ("#f97316", "#7c2d12", "#fdba74"),
            "low": ("#eab308", "#713f12", "#fde047")
        }
        border_color, bg_color, text_color = colors.get(severity, ("#6b7280", "#374151", "#d1d5db"))

        signal_key = signal.get('signal', 'Unknown')
        signal_name = SIGNAL_NAMES.get(signal_key, signal_key.replace('_', ' ').title())

        html += f"""
        <div style='margin-bottom: 12px; padding: 14px; background: {bg_color}; border-left: 4px solid {border_color}; border-radius: 8px;'>
            <span style='color: {border_color}; font-weight: 600; font-size: 0.75em; text-transform: uppercase; letter-spacing: 0.05em;'>{severity}</span>
            <div style='color: #f3f4f6; font-weight: 500; margin-top: 4px;'>{signal_name}</div>
            <div style='color: #9ca3af; font-size: 0.9em; margin-top: 4px;'>{signal.get('detail', '')}</div>
        </div>
        """
    html += "</div>"
    return html


def format_concerns_html(concerns: list) -> str:
    """Format key concerns as HTML."""
    if not concerns:
        return "<div class='fixed-tab-content'><p style='color: #9ca3af; padding: 16px;'>No specific concerns identified</p></div>"

    html = "<div class='fixed-tab-content'>"
    for concern in concerns:
        html += f"""
        <div style='margin-bottom: 12px; padding: 14px; background: #7f1d1d; border-radius: 8px; border: 1px solid #991b1b;'>
            <div style='color: #fca5a5; font-weight: 600;'>⚠️ {concern.get('concern', 'Unknown')}</div>
            <div style='color: #d1d5db; font-size: 0.9em; margin-top: 8px;'>
                <span style='color: #9ca3af;'>Evidence:</span> {concern.get('evidence', 'N/A')[:200]}...
            </div>
        </div>
        """
    html += "</div>"
    return html


def format_positives_html(positives: list) -> str:
    """Format mitigating factors as HTML."""
    if not positives:
        return "<div class='fixed-tab-content'><p style='color: #9ca3af; padding: 16px;'>No mitigating factors identified</p></div>"

    html = "<div class='fixed-tab-content' style='padding: 8px;'>"
    for positive in positives:
        html += f"""
        <div style='display: flex; align-items: flex-start; margin-bottom: 10px;'>
            <span style='color: #22c55e; margin-right: 8px;'>✓</span>
            <span style='color: #d1d5db;'>{positive}</span>
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
            <div style='color: #d1d5db; margin-top: 8px;'>{str(e)}</div>
        </div>
        """
        yield (error_html, EMPTY_SCORE, EMPTY_VERDICT, EMPTY_METRICS, EMPTY_TAB_CONTENT, EMPTY_TAB_CONTENT, EMPTY_TAB_CONTENT, EMPTY_TAB_CONTENT)
        return

    if "error" in result:
        error_html = f"""
        <div class="fixed-header" style='text-align: center; padding: 30px; background: #7f1d1d; border-radius: 12px; border: 1px solid #991b1b;'>
            <div style='color: #fca5a5; font-size: 1.2em; font-weight: 600;'>⚠️ Error</div>
            <div style='color: #d1d5db; margin-top: 8px;'>{result['error']}</div>
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

    # Colors
    color = get_score_color(score)
    bg_color = get_score_bg(score)
    emoji = get_classification_emoji(classification)

    # Format header with venue info
    review_count = meta.get('place_review_count', 0)
    review_str = f"{review_count:,}" if isinstance(review_count, int) else str(review_count)

    header_html = f"""
    <div class="fixed-header" style='text-align: center; padding: 16px; background: #1f2937; border-radius: 10px; border: 1px solid #374151;'>
        <h2 style='margin: 0; color: #f3f4f6; font-size: 1.3em;'>{meta.get('place_name', query)}</h2>
        <p style='color: #9ca3af; margin: 6px 0 0 0; font-size: 0.85em;'>{meta.get('place_address', 'Address not available')}</p>
        <div style='margin-top: 8px; display: flex; justify-content: center; align-items: center; gap: 8px;'>
            <span style='color: #fbbf24;'>★ {meta.get('place_rating', 'N/A')}</span>
            <span style='color: #6b7280;'>•</span>
            <span style='color: #9ca3af; font-size: 0.9em;'>{review_str} reviews</span>
        </div>
    </div>
    """

    # Format score display
    score_html = f"""
    <div class="fixed-score" style='text-align: center; padding: 20px; background: linear-gradient(135deg, #111827 0%, #1f2937 100%); border-radius: 10px; border: 1px solid #374151;'>
        <div style='font-size: 3em; font-weight: 700; color: {color}; text-shadow: 0 0 30px {color}40;'>
            {emoji} {score}
        </div>
        <div style='font-size: 0.85em; color: #9ca3af; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.1em;'>
            Tourist Trap Score
        </div>
        <div style='margin-top: 12px;'>
            <span style='padding: 6px 16px; background: {bg_color}; color: {color}; border-radius: 16px; font-weight: 600; font-size: 0.8em; border: 1px solid {color};'>
                {classification.replace('_', ' ').upper()}
            </span>
        </div>
        <div style='color: #6b7280; margin-top: 8px; font-size: 0.8em;'>
            Confidence: <span style='color: #9ca3af;'>{confidence.upper()}</span>
        </div>
    </div>
    """

    # Format verdict quote
    verdict_html = f"""
    <div class="fixed-verdict" style='padding: 14px; background: {bg_color}; border-radius: 10px; border-left: 4px solid {color};'>
        <p style='font-size: 1em; margin: 0; font-style: italic; color: #f3f4f6; line-height: 1.5;'>
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
        if is_negative and value > 0:
            val_color = "#ef4444"
            bg = "#7f1d1d"
            border = "#991b1b"
        elif not is_negative and value > 0:
            val_color = "#22c55e"
            bg = "#14532d"
            border = "#166534"
        else:
            val_color = "#9ca3af"
            bg = "#1f2937"
            border = "#374151"

        return f"""
        <div style='padding: 10px; background: {bg}; border-radius: 8px; text-align: center; border: 1px solid {border};'>
            <div style='font-size: 1.5em; font-weight: 700; color: {val_color};'>{value}</div>
            <div style='font-size: 0.7em; color: #9ca3af; margin-top: 2px;'>{label}</div>
        </div>
        """

    # Credibility gap special handling
    cred_color = "#ef4444" if cred_gap < -5 else "#22c55e" if cred_gap > 5 else "#9ca3af"
    cred_bg = "#7f1d1d" if cred_gap < -5 else "#14532d" if cred_gap > 5 else "#1f2937"
    cred_border = "#991b1b" if cred_gap < -5 else "#166534" if cred_gap > 5 else "#374151"

    metrics_html = f"""
    <div class="fixed-metrics" style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px;'>
        {metric_card(trap_warnings, "Trap Warnings")}
        {metric_card(fake_claims, "Fake Review Claims")}
        {metric_card(local_guides, "Local Guides Warning")}
        <div style='padding: 10px; background: {cred_bg}; border-radius: 8px; text-align: center; border: 1px solid {cred_border};'>
            <div style='font-size: 1.5em; font-weight: 700; color: {cred_color};'>{cred_gap:+.0f}</div>
            <div style='font-size: 0.7em; color: #9ca3af; margin-top: 2px;'>Credibility Gap</div>
        </div>
    </div>
    """

    signals_html = format_signals_html(signals)
    concerns_html = format_concerns_html(concerns)
    positives_html = format_positives_html(positives)

    # Full analysis as HTML
    analysis_html = f"""
    <div class="fixed-tab-content" style='padding: 20px; color: #d1d5db; line-height: 1.7;'>
        <div style='font-weight: 600; color: #f3f4f6; margin-bottom: 12px;'>Recommendation: {recommendation}</div>
        <hr style='border: none; border-top: 1px solid #374151; margin: 16px 0;'>
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


# Build UI
with gr.Blocks(title="TrapCheck") as app:
    # Inject CSS and header
    gr.HTML(f"""
    <style>{CUSTOM_CSS}</style>
    <div class="header-container">
        <h1 class="logo-title">
            <span class="logo-emoji">🎯</span>
            <span class="logo-text">TrapCheck</span>
        </h1>
        <p class="tagline">Detect tourist traps before they catch you</p>
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
        head="<title>TrapCheck</title>",
    )
