# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**TrapCheck** - A tourist trap detector that analyzes Google Maps reviews using computed metrics + Google AI (Gemini) API to determine if a restaurant/venue is a tourist trap.

## Development Commands

```bash
# Setup (one-time)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run Web UI (Gradio)
python app.py

# Run CLI
python main.py "Restaurant Name" "City"
python main.py "Pizzeria Da Michele" "Naples"

# Mock mode (no SerpAPI key needed)
# Just omit SERPAPI_KEY from .env - app falls back to mock data automatically
```

## Configuration

Copy `.env.example` to `.env`:
- `GOOGLE_API_KEY` - Required for Gemini analysis
- `SERPAPI_KEY` - Optional; uses mock data if not set

## Architecture

### Data Flow
```
User Input → search_place() → fetch_stratified_reviews()
                                    ↓
                         compute_metrics() [pre-computed signals]
                                    ↓
                         Gemini API [interprets metrics, generates verdict]
                                    ↓
                         Structured JSON → UI
```

### Key Design Decision
Metrics are computed BEFORE the LLM sees the data (`src/metrics.py`). This prevents the model from being influenced by raw reviews and ensures consistent quantitative signals:
- Reviewer credibility scores (based on review count, Local Guide status, photos)
- Keyword detection (trap warnings, manipulation accusations, quality complaints)
- Date clustering analysis (detects review manipulation patterns)
- Credibility inversion (when negative reviewers are more credible than positive)

### Module Structure

| File | Purpose |
|------|---------|
| `app.py` | Gradio web UI with dark theme |
| `main.py` | CLI entry point |
| `src/analyzer.py` | Core analysis pipeline, Gemini prompt construction |
| `src/metrics.py` | Pre-LLM metrics computation (credibility, keywords, signals) |
| `src/tools/serpapi.py` | Google Maps place search and review fetching |
| `src/tools/mock_data.py` | Development data (Da Michele, Olive Garden, Katz's, Hard Rock) |
| `src/config.py` | Environment variable loading and validation |

### Signal Detection

Signals computed in `src/metrics.py` before Gemini analysis:
- `credibility_inversion` - Negative reviewers more credible than positive
- `explicit_trap_warnings` - Reviews containing "tourist trap", "scam", etc.
- `manipulation_accusations` - Reviews claiming fake/bought reviews
- `review_clustering` - Many positive reviews on same days (manipulation indicator)
- `local_guide_warnings` - Local Guides disproportionately in negative reviews
- `service_food_disparity` - High service ratings but low food ratings

### Output Schema

Gemini returns JSON with:
- `tourist_trap_score` (0-100), `confidence`, `classification`
- `verdict` (one-liner), `recommendation`, `reasoning`
- `key_concerns` with evidence quotes
- `mitigating_factors` (positives)

## Mock Data

Four pre-configured venues in `src/tools/mock_data.py` for testing without SerpAPI:
- "Pizzeria Da Michele" (Naples) - Authentic, not a trap
- "Olive Garden Times Square" - Classic tourist trap
- "Hard Rock Cafe Rome" - Tourist trap
- "Katz's Delicatessen" (NYC) - Famous but authentic

## RAG System

RAG integration provides similar venue examples for calibration:
- **Database:** `RAG/rag_master.json` (149 examples)
- **Module:** `src/rag/retriever.py`
- **Dependencies:** `chromadb`, `sentence-transformers`

```bash
# Test RAG retriever
python -m src.rag.retriever

# Run variance tests
python scripts/variance_test.py --runs 5
```

## Testing & Experiments

Variance testing framework in `scripts/`:
- `variance_test.py` - Runs N analyses per venue, computes statistics
- Results go to `docs/experiments/`

```bash
# Full test (5 runs x 4 venues)
python scripts/variance_test.py --output docs/experiments/baseline.json

# Single venue test
python scripts/variance_test.py --venue "da michele" --runs 3
```

## Documentation

- `docs/PROJECT_JOURNAL.md` - Development log, decisions, experiment results
- `docs/EXECUTION_PLAN.md` - Phase-by-phase implementation plan
- `docs/experiments/` - Experiment results and analysis

## Optional Features (Not Yet Implemented)

- `playwright` - For screenshot capture
