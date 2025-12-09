#!/usr/bin/env python3
"""
Tourist Trap Detector - Gradio Web UI
"""
import gradio as gr
from src.config import validate_config
from src.analyzer import analyze_venue


def get_score_color(score: int) -> str:
    """Get color based on trap score."""
    if score >= 80:
        return "#dc2626"  # red
    elif score >= 60:
        return "#ea580c"  # orange
    elif score >= 40:
        return "#ca8a04"  # yellow
    elif score >= 20:
        return "#65a30d"  # lime
    else:
        return "#16a34a"  # green


def get_classification_emoji(classification: str) -> str:
    """Get emoji for classification."""
    emojis = {
        "definite_trap": "🚨",
        "likely_trap": "⚠️",
        "possibly_trap": "🤔",
        "unclear": "❓",
        "likely_authentic": "✅",
        "verified_authentic": "💚",
    }
    return emojis.get(classification, "❓")


def format_signals_html(signals: list) -> str:
    """Format detected signals as HTML."""
    if not signals:
        return "<p style='color: #666;'>No significant signals detected</p>"

    html = ""
    for signal in signals:
        severity = signal.get("severity", "medium")
        color = {"high": "#dc2626", "medium": "#ea580c", "low": "#ca8a04"}.get(severity, "#666")
        html += f"""
        <div style='margin-bottom: 12px; padding: 10px; background: #f9fafb; border-left: 4px solid {color}; border-radius: 4px;'>
            <strong style='color: {color};'>[{severity.upper()}]</strong> {signal.get('signal', 'Unknown')}
            <br><span style='color: #666; font-size: 0.9em;'>{signal.get('detail', '')}</span>
        </div>
        """
    return html


def format_concerns_html(concerns: list) -> str:
    """Format key concerns as HTML."""
    if not concerns:
        return "<p style='color: #666;'>No specific concerns identified</p>"

    html = ""
    for concern in concerns:
        html += f"""
        <div style='margin-bottom: 12px; padding: 10px; background: #fef2f2; border-radius: 4px;'>
            <strong style='color: #dc2626;'>⚠️ {concern.get('concern', 'Unknown')}</strong>
            <br><span style='color: #666; font-size: 0.9em;'>Evidence: {concern.get('evidence', 'N/A')[:200]}...</span>
        </div>
        """
    return html


def format_positives_html(positives: list) -> str:
    """Format mitigating factors as HTML."""
    if not positives:
        return "<p style='color: #666;'>No mitigating factors identified</p>"

    html = "<ul style='margin: 0; padding-left: 20px;'>"
    for positive in positives:
        html += f"<li style='color: #16a34a; margin-bottom: 4px;'>{positive}</li>"
    html += "</ul>"
    return html


def analyze(query: str, location: str, progress=gr.Progress()) -> tuple:
    """Run analysis and return formatted results."""
    if not query.strip():
        return (
            "Please enter a restaurant name",
            "", "", "", "", "", "", ""
        )

    progress(0.1, desc="Searching for venue...")

    try:
        location_clean = location.strip() if location else None
        result = analyze_venue(query.strip(), location_clean)
    except Exception as e:
        return (
            f"Error: {str(e)}",
            "", "", "", "", "", "", ""
        )

    if "error" in result:
        return (
            f"Error: {result['error']}",
            "", "", "", "", "", "", ""
        )

    progress(1.0, desc="Analysis complete!")

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

    # Format header
    emoji = get_classification_emoji(classification)
    color = get_score_color(score)

    header_html = f"""
    <div style='text-align: center; padding: 20px;'>
        <h2 style='margin: 0;'>{meta.get('place_name', query)}</h2>
        <p style='color: #666; margin: 5px 0;'>{meta.get('place_address', 'Address not available')}</p>
        <p style='margin: 5px 0;'>
            <span style='font-size: 1.2em;'>⭐ {meta.get('place_rating', 'N/A')}</span>
            <span style='color: #666;'> ({meta.get('place_review_count', 'N/A'):,} reviews)</span>
        </p>
    </div>
    """

    # Format score display
    score_html = f"""
    <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px;'>
        <div style='font-size: 4em; font-weight: bold; color: {color};'>{emoji} {score}</div>
        <div style='font-size: 1.2em; color: #666; margin-top: 10px;'>Tourist Trap Score</div>
        <div style='margin-top: 15px; padding: 8px 16px; background: {color}; color: white; border-radius: 20px; display: inline-block;'>
            {classification.replace('_', ' ').upper()}
        </div>
        <div style='color: #666; margin-top: 10px;'>Confidence: {confidence.upper()}</div>
    </div>
    """

    # Format verdict
    verdict_html = f"""
    <div style='padding: 20px; background: #f8fafc; border-radius: 8px; border-left: 4px solid {color};'>
        <p style='font-size: 1.1em; margin: 0; font-style: italic;'>"{verdict}"</p>
    </div>
    """

    # Format metrics summary
    metrics_html = f"""
    <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px;'>
        <div style='padding: 10px; background: #f1f5f9; border-radius: 8px; text-align: center;'>
            <div style='font-size: 1.5em; font-weight: bold;'>{metrics.get('trap_warning_count', 0)}</div>
            <div style='font-size: 0.8em; color: #666;'>Trap Warnings</div>
        </div>
        <div style='padding: 10px; background: #f1f5f9; border-radius: 8px; text-align: center;'>
            <div style='font-size: 1.5em; font-weight: bold;'>{metrics.get('manipulation_accusation_count', 0)}</div>
            <div style='font-size: 0.8em; color: #666;'>Fake Review Claims</div>
        </div>
        <div style='padding: 10px; background: #f1f5f9; border-radius: 8px; text-align: center;'>
            <div style='font-size: 1.5em; font-weight: bold;'>{metrics.get('local_guides_in_negative', 0)}</div>
            <div style='font-size: 0.8em; color: #666;'>Local Guides Warning</div>
        </div>
        <div style='padding: 10px; background: #f1f5f9; border-radius: 8px; text-align: center;'>
            <div style='font-size: 1.5em; font-weight: bold;'>{metrics.get('credibility_gap', 0):+.0f}</div>
            <div style='font-size: 0.8em; color: #666;'>Credibility Gap</div>
        </div>
    </div>
    """

    signals_html = format_signals_html(signals)
    concerns_html = format_concerns_html(concerns)
    positives_html = format_positives_html(positives)

    return (
        header_html,
        score_html,
        verdict_html,
        metrics_html,
        signals_html,
        concerns_html,
        positives_html,
        f"**Recommendation:** {recommendation}\n\n{reasoning}",
    )


# Build UI
with gr.Blocks() as app:
    gr.Markdown("# 🎯 Tourist Trap Detector", elem_classes="main-title")
    gr.Markdown(
        "*Find out if that restaurant is worth your money, or just another tourist trap.*",
        elem_classes="subtitle"
    )

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
        with gr.Column(scale=1):
            analyze_btn = gr.Button("🔍 Analyze", variant="primary", size="lg")

    with gr.Row():
        with gr.Column(scale=1):
            header_output = gr.HTML(label="Venue")
            score_output = gr.HTML(label="Score")
            metrics_output = gr.HTML(label="Key Metrics")

        with gr.Column(scale=2):
            verdict_output = gr.HTML(label="Verdict")

            with gr.Tabs():
                with gr.Tab("🚨 Detected Signals"):
                    signals_output = gr.HTML()
                with gr.Tab("⚠️ Key Concerns"):
                    concerns_output = gr.HTML()
                with gr.Tab("✅ Positives"):
                    positives_output = gr.HTML()
                with gr.Tab("📝 Full Analysis"):
                    analysis_output = gr.Markdown()

    # Examples
    gr.Examples(
        examples=[
            ["Ristorante Luigi Cantina e Cucina", "Rome"],
            ["Pizzeria Da Michele", "Naples"],
            ["Katz's Delicatessen", "New York"],
            ["Joe's Pizza", "New York"],
        ],
        inputs=[query_input, location_input],
        label="Try these examples:",
    )

    # Connect
    analyze_btn.click(
        fn=analyze,
        inputs=[query_input, location_input],
        outputs=[
            header_output,
            score_output,
            verdict_output,
            metrics_output,
            signals_output,
            concerns_output,
            positives_output,
            analysis_output,
        ],
    )

    # Also trigger on Enter
    query_input.submit(
        fn=analyze,
        inputs=[query_input, location_input],
        outputs=[
            header_output,
            score_output,
            verdict_output,
            metrics_output,
            signals_output,
            concerns_output,
            positives_output,
            analysis_output,
        ],
    )


if __name__ == "__main__":
    try:
        validate_config()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set up your .env file with API keys.")
        exit(1)

    app.launch(share=False)
