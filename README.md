# TrapCheck - Tourist Trap Detector

An AI-powered system that analyzes Google Maps reviews to determine if a venue is a "tourist trap." Built as a course project for Applied Language Models.

**Author:** Omri Ashkenazi

## Project Summary

TrapCheck uses a hybrid NLP architecture combining pre-computed metrics with Large Language Model interpretation to analyze venues. Unlike pure LLM approaches that suffer from inconsistent analysis, TrapCheck computes quantitative signals (reviewer credibility, keyword detection, date clustering) *before* the LLM sees any data, ensuring consistent and reliable assessments.

**Supported Venue Types:** Restaurants, cafes, bars, museums, attractions, tours, shops, and markets.

### Key Features

- **Pre-computed Metrics:** Deterministic signal detection for reviewer credibility, trap warnings, manipulation accusations, and review clustering patterns
- **RAG-Enhanced Scoring:** Keyword-based retrieval of similar venues for score calibration (32% MAE reduction, 95.6% accuracy)
- **Multi-Source Analysis:** Combines Google Maps reviews with external signals (Reddit, TripAdvisor forums)
- **Venue-Agnostic:** Automatically detects venue type and applies specialized analysis

## Architecture

```
User Input → Search Place → Detect Venue Type → Fetch Reviews
                                                     ↓
                                    ┌────────────────────────────┐
                                    │   Pre-computed Metrics     │ ← DETERMINISTIC
                                    │   (src/metrics.py)         │
                                    │   • Credibility scores     │
                                    │   • Keyword detection      │
                                    │   • Date clustering        │
                                    │   • Language analysis      │
                                    └────────────────────────────┘
                                                     ↓
                                    ┌────────────────────────────┐
                                    │   RAG Calibration          │
                                    │   (src/rag/retriever_      │
                                    │    lightweight.py)         │
                                    │   • Similar venue examples │
                                    │   • Score reference points │
                                    └────────────────────────────┘
                                                     ↓
                                    ┌────────────────────────────┐
                                    │   Gemini LLM               │ ← CONSTRAINED
                                    │   (JSON schema output)     │   (structured output)
                                    │   • Interprets metrics     │
                                    │   • Generates verdict      │
                                    └────────────────────────────┘
                                                     ↓
                                    Structured JSON → Web UI / CLI
```

**Key Design Decision:** Computing metrics before LLM analysis ensures 100% signal stability across runs while allowing the model to focus on interpretation.

## Dataset Description

### RAG Database (`src/rag/data/rag_master.json`)

A curated dataset of **149 global venues** classified as Tourist Traps, Local Gems, or Mixed:

| Category | Count | Description |
|----------|-------|-------------|
| Restaurants | 55 | Fine dining to street food |
| Attractions | 39 | Museums, landmarks, viewpoints |
| Cafes | 15 | Coffee houses, tea rooms |
| Street Food | 13 | Markets, food stalls |
| Markets | 13 | Souvenirs, local goods |
| Bars | 11 | Pubs, cocktail bars |
| Tours | 3 | Walking tours, experiences |

**Verdict Distribution:**
- Tourist Traps: ~50 entries (score 60-95)
- Local Gems: ~50 entries (score 5-35)
- Mixed: ~49 entries (score 35-65)

**Sources:** Travel forums (TripAdvisor, Lonely Planet), Reddit (r/travel, r/food, city subreddits), food blogs, local review sites.

### Evaluation Dataset

For reproducible evaluation, we created **mock review data** for 4 venues representing different categories. Ground truth scores were manually assigned based on expert knowledge and public reputation:

| Venue | Location | Category | Ground Truth Score | Rationale |
|-------|----------|----------|-------------------|-----------|
| Pizzeria Da Michele | Naples | Authentic | 25 | Historic pizzeria, local institution, UNESCO-recognized |
| Olive Garden Times Square | NYC | Tourist Trap | 85 | Chain restaurant in tourist hotspot, known trap |
| Carlo Menta | Rome | Mixed | 50 | Near Vatican, mixed reviews, some tourist trap signals |
| Katz's Delicatessen | NYC | Mixed | 35 | Famous landmark, high prices but genuine quality |

**Note:** Mock data allows controlled experiments without API costs. Each venue's mock reviews were crafted to reflect real-world review patterns (credibility distribution, keyword presence, rating spread).

## Model & Methods

### 1. Pre-computed Metrics Layer

The metrics layer (`src/metrics.py`) computes signals deterministically before LLM analysis:

**Reviewer Credibility Scoring:**
- Based on review count, Local Guide status, photo contributions
- Separate averages for positive vs negative reviewers
- "Credibility inversion" signal when negative reviewers are more credible

**Keyword Detection:**
- Trap awareness keywords: "tourist trap", "scam", "rip off", "avoid"
- Manipulation keywords: "fake review", "paid review", "forced to review"
- Quality complaints: Venue-specific (food issues for restaurants, crowd/wait for attractions)

**Date Clustering Analysis:**
- Detects suspicious patterns of positive reviews on same days
- Indicates potential review manipulation

**Language Analysis:**
- Detects tourist vs local language patterns
- Flags venues where credibility differs by reviewer language

### 2. RAG Pipeline

**Keyword-based RAG** (`src/rag/retriever_lightweight.py`) - Production default:
- Jaccard-like keyword overlap scoring
- Retrieves 6 examples per query (2 traps, 2 gems, 2 mixed)
- No external dependencies (pure Python)
- ~0.1s latency overhead

**Vector RAG** (`src/rag/retriever.py`) - Alternative for larger datasets:
- ChromaDB vector store with `all-MiniLM-L6-v2` embeddings
- Cosine similarity search
- Better semantic understanding at scale
- ~0.9s latency overhead

### 3. LLM Integration (Gemini 2.0 Flash)

- **Structured JSON Output:** Schema-constrained responses ensure consistent output format
- **Few-shot Context:** RAG examples provide score calibration reference points
- **Temperature:** Default (deterministic due to JSON schema constraints)

## Results

### Evaluation Framework (v2)

Evaluated on a **30-venue stratified test set** sampled from the RAG database:
- 10 tourist traps, 10 local gems, 10 mixed venues
- 3 runs per venue (90 total runs per experiment)
- Leave-one-out evaluation (test venue excluded from RAG retrieval)
- Synthetic reviews with realistic noise to prevent overfitting

### Evaluation Metrics

| Configuration | Category Accuracy | Within ±15 | MAE | StdDev |
|---------------|------------------|------------|-----|--------|
| Baseline (no RAG) | 90.0% | 77.8% | 13.6 | 3.27 |
| temp_0.0 | 90.0% | 84.4% | 12.7 | 1.64 |
| **RAG Keyword** | **95.6%** | **93.3%** | **9.3** | **1.38** |
| RAG Vector | 94.4% | 93.3% | 9.9 | 2.06 |

### Key Findings

1. **RAG Keyword achieves 32% reduction in MAE** (13.6 → 9.3) with minimal latency overhead
2. **95.6% category accuracy** with RAG keyword (vs 90% baseline)
3. **Mixed venues dramatically improved:** 70% → 90% accuracy with RAG
4. **100% signal stability** - same signals detected every run (validates pre-computed approach)
5. **Temperature has minimal effect** - all temps achieve 90% accuracy; temp_0.0 only reduces variance

### Per-Category Results (RAG Keyword)

| Category | Accuracy | Notes |
|----------|----------|-------|
| tourist_trap | 97% | Excellent detection |
| local_gem | 100% | Perfect classification |
| mixed | 90% | Major improvement from 70% baseline |

**Key Insight:** RAG provides crucial calibration for ambiguous "mixed" venues where the model previously struggled.

### Qualitative Examples

**Example 1: Pizzeria Da Michele (Naples) - Verified Authentic**
```
Score: 20/100 | Classification: VERIFIED AUTHENTIC
Verdict: "A legendary pizzeria with genuine local following and exceptional pizza quality."

Key Signals:
- High credibility positive reviewers (avg 78/100)
- Local Guide endorsements: 12
- Explicit trap warnings: 0
- Language analysis: Italian reviewers highly positive

Recommendation: Worth the wait - arrive early or late to avoid queues.
```

**Example 2: Olive Garden Times Square (NYC) - Definite Trap**
```
Score: 95/100 | Classification: DEFINITE TRAP
Verdict: "A textbook tourist trap capitalizing on Times Square foot traffic."

Key Signals:
- Credibility inversion detected (negative reviewers more credible)
- Explicit trap warnings: 8
- Tourist hotspot location score: 95/100
- External negative reputation (Reddit, TripAdvisor)

Recommendation: Avoid - countless better options within walking distance.
```

## Setup Instructions

### Requirements

- Python 3.10+
- Google AI API key (free at [aistudio.google.com](https://aistudio.google.com/apikey))
- SerpAPI key (optional - mock data works without it)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/trapcheck.git
cd trapcheck

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY (required)
# SERPAPI_KEY is optional - mock data works without it
```

### Running the Application

**Web UI (Gradio):**
```bash
python app.py
# Opens at http://localhost:7860
```

**CLI:**
```bash
python main.py "Restaurant Name" "City"
python main.py "Pizzeria Da Michele" "Naples"
```

**Mock Mode:**
Omit `SERPAPI_KEY` from `.env` to use built-in mock data for testing:
- Pizzeria Da Michele (Naples) - Authentic
- Olive Garden Times Square (NYC) - Tourist Trap
- Carlo Menta (Rome) - Mixed
- Katz's Delicatessen (NYC) - Mixed

### Running Evaluations

```bash
# v2 evaluation (recommended): 30 venues x 3 runs = 90 total
python scripts/evaluation_v2.py --name my_test --rag --rag-mode keyword

# Baseline comparison
python scripts/evaluation_v2.py --name baseline

# v1 evaluation (legacy): 4 mock venues
python scripts/evaluation.py --name my_test --runs 5 --rag --rag-mode keyword

# Results saved to docs/experiments/v2/ (or v1/ for legacy)
```

## Project Structure

```
trapcheck/
├── app.py                      # Gradio web UI
├── main.py                     # CLI interface
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── src/
│   ├── analyzer.py            # Core analysis pipeline
│   ├── metrics.py             # Pre-computed metrics layer
│   ├── config.py              # Configuration loader
│   ├── rag/
│   │   ├── retriever.py           # Vector RAG (ChromaDB)
│   │   ├── retriever_lightweight.py  # Keyword RAG (production)
│   │   └── data/
│   │       └── rag_master.json    # 149-entry RAG database
│   └── tools/
│       ├── serpapi.py         # Google Maps API wrapper
│       ├── mock_data.py       # Test data
│       └── web_search.py      # External signals
├── scripts/
│   ├── evaluation.py          # v1 evaluation (4 mock venues)
│   └── evaluation_v2.py       # v2 evaluation (30 RAG venues)
├── docs/
│   ├── PROJECT_JOURNAL.md     # Development log
│   └── experiments/
│       ├── v1/                # Archived v1 results (4 venues)
│       └── v2/                # Current v2 results (30 venues)
│           ├── baseline.json
│           ├── rag_keyword.json
│           └── rag_vector.json
└── static/
    └── favicon.svg
```

## Limitations

1. **Edge Cases:** Some venues (e.g., Harry's Bar Venice) are persistently misclassified across all experiments
2. **Synthetic Evaluation:** While v2 uses 30 venues with realistic noise, results are on synthetic reviews; real-world performance may vary
3. **English-centric:** Best performance on English reviews; language detection helps but coverage varies
4. **RAG Database Size:** 149 examples may not cover all venue types equally (tours underrepresented with only 3 examples)

## Acknowledgments

- Google AI for Gemini API access
- SerpAPI for Google Maps data extraction
- Course instructors for guidance on LLM evaluation methodology

---

**Course:** Applied Language Models
**Project:** Tourist Trap Detector with RAG Enhancement
**Date:** December 2024
