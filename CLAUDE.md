# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tourist Trap Detector** - An agentic AI system that analyzes restaurants/venues to predict whether they are "tourist traps" (establishments exploiting tourist traffic with inflated prices and lower quality).

**Approach:** Agentic AI with RAG enhancement, designed as a 2-week university course project on Applied Language Models.

## Technical Stack

- **Language Model:** Claude API with tool-use capabilities
- **Web UI:** Gradio
- **Vector Database:** ChromaDB (local)
- **Embeddings:** sentence-transformers/all-MiniLM-L6-v2
- **Web Scraping:** Playwright (screenshots)
- **External APIs:** SerpAPI (Google Maps reviews), optionally Outscraper
- **Runtime:** Google Colab notebook

## Architecture

The system follows an agent-orchestrator pattern:
1. User provides business name + location OR Google Maps URL
2. Claude orchestrates tool calls to gather data
3. RAG retrieves similar labeled examples for few-shot context
4. Claude generates structured analysis with evidence
5. Gradio UI displays results with tabs for red flags, positives, and evidence

### Agent Tools (5 total)

| Tool | Purpose |
|------|---------|
| `search_place` | Find venue on Google Maps via SerpAPI |
| `fetch_reviews` | Get paginated reviews (up to 50) via SerpAPI |
| `web_search` | Additional context search (Reddit, travel forums) |
| `capture_screenshot` | Visual evidence via Playwright |
| `retrieve_similar_examples` | RAG similarity search in ChromaDB |

### Key Data Flow

```
User Input → search_place → fetch_reviews → retrieve_similar_examples
                                ↓
                    capture_screenshot + web_search
                                ↓
                    Claude Analysis (with RAG context)
                                ↓
                    Structured JSON Output → Gradio UI
```

## Project Structure (Planned)

```
tourist-trap-detector/
├── data/
│   ├── rag_examples.json      # 50-100 labeled examples
│   └── test_set.json          # 30 venues for evaluation
├── src/
│   ├── agent.py               # Claude API tool orchestration
│   ├── tools/                 # Tool implementations
│   ├── rag_database.py        # ChromaDB setup/seeding
│   ├── output_formatter.py    # Result JSON structure
│   └── ui.py                  # Gradio interface
├── notebooks/
│   └── tourist_trap_detector.ipynb
└── results/
```

## Key Specifications

### SerpAPI Review Fetching Pattern
```python
# 1. Search for place
GET /search?engine=google_maps&q=restaurant+name+city
# 2. Extract data_id from results
# 3. Fetch reviews with pagination using next_page_token
GET /search?engine=google_maps_reviews&data_id={data_id}
```

### RAG Database
- Collection: `tourist_trap_examples`
- 50-100 curated examples labeled as `tourist_trap`, `local_gem`, or `mixed`
- Documents include: name, location, verdict, summary, red_flags, positive_signals, sample_reviews

### Output Schema
The analysis returns structured JSON with:
- `verdict`: tourist_trap_score (0-100), confidence, classification, one_liner
- `evidence`: red_flags and positive_signals with supporting quotes
- `context`: location_risk, price_tier, comparable_alternatives
- `visuals`: screenshots, rating distribution

## Tourist Trap Detection Criteria

**Red Flags:** price-quality mismatch, authenticity issues, "locals don't come here", rushed service, quality decline, location dependency, review manipulation

**Positive Signals:** local endorsement, value acknowledgment, authenticity praise, repeat visitors, specific quality praise

## Cost Estimates

~$0.06 per query (SerpAPI + Claude Sonnet)

## Reference Document

The complete specification is in `trapcheck.md` (825 lines) containing:
- Full tool JSON schemas
- RAG document schema with ChromaDB implementation examples
- Gradio UI mockup and implementation skeleton
- 7-phase implementation checklist
- Evaluation framework with test set design
- Known limitations and mitigations

## External Documentation

- [SerpAPI Google Maps Reviews](https://serpapi.com/google-maps-reviews-api)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Gradio](https://www.gradio.app/docs)
- [ChromaDB](https://docs.trychroma.com/)
- [Playwright Python](https://playwright.dev/python/)
