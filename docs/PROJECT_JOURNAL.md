# TrapCheck Project Journal

## Project Overview

**Project Name:** TrapCheck (Tourist Trap Detector)
**Course:** Applied Language Models (2-week university course)
**Approach:** Agentic AI with RAG Enhancement
**Author:** [Your Name]
**Started:** December 2024

---

## Executive Summary

TrapCheck is an AI-powered system that analyzes Google Maps reviews to determine if a venue is a "tourist trap." Supports restaurants, museums, attractions, tours, and shops. The system uses a two-stage architecture:

1. **Pre-computed Metrics** (`src/metrics.py`): Quantitative signals extracted from reviews before LLM analysis
2. **LLM Interpretation** (Gemini 2.5 Flash): Interprets metrics and generates human-readable verdicts

**Key Innovation:** Computing signals *before* the LLM sees raw data ensures consistent quantitative analysis while allowing the LLM to focus on interpretation and explanation.

---

## Development Timeline

### Phase 1: Research & Design (Completed)

- Created comprehensive project specification (`trapcheck.md`)
- Defined tourist trap indicators (red flags and positive signals)
- Designed technical architecture (Agent Orchestrator + Tools + RAG + UI)
- Identified API constraints (Google Places API 5-review limit → SerpAPI solution)

### Phase 2: MVP Implementation (Completed)

- Implemented core analyzer pipeline (`src/analyzer.py`)
- Built metrics computation layer (`src/metrics.py`)
- Created SerpAPI integration with mock data fallback
- Built Gradio web UI with dark theme styling
- **Status:** Functional POC with working analysis pipeline

### Phase 3: RAG Database Creation (Completed)

- Built 149-example RAG database (`RAG/rag_master.json`)
- Categories: Tourist Traps, Local Gems, Mixed
- Sources: Travel forums, Reddit, review sites
- Created via Gemini-assisted curation in 4 batches

### Phase 4: RAG Integration & Testing (Current)

- **Status:** Baseline measured, RAG module created, integration pending
- **Goal:** Use similar examples as few-shot context for the analyzer
- **Expected Impact:** Improved consistency, reduced score variance

---

## Current Challenges

### Issue #1: Score Variance Between Runs (MEASURED)

**Problem:** Running the same mock data produces varying tourist trap scores across runs.

**Baseline Measurement (2024-12-14):**
| Venue | Score Range | StdDev | Classification Consistency |
|-------|-------------|--------|---------------------------|
| Da Michele | 20-35 | 5.48 | 60% (split verified/likely) |
| Olive Garden | 85-92 | 3.51 | 100% (definite_trap) |
| Katz's | 15-25 | 4.18 | 100% (verified_authentic) |

**Key Finding:** Variance correlates with signal ambiguity, not inherent LLM randomness:
- Clear traps/gems have low variance (3-4 StdDev)
- Ambiguous venues have higher variance (5+ StdDev)
- Classification is more stable than raw scores (87% avg consistency)

**Updated Solutions (prioritized):**
1. ~~Temperature control~~ - Lower priority, baseline shows reasonable consistency
2. **RAG integration** - Focus on ambiguous cases like Da Michele
3. Scoring rubric - Consider if RAG alone is insufficient

---

## Experiment Log

### Experiment 1: Baseline Variance Measurement

**Date:** 2024-12-14
**Status:** COMPLETED
**Objective:** Establish baseline score variance on mock data

**Results Summary:**
- **Avg StdDev:** 4.39 (better than expected)
- **Avg Score Range:** 10.67 points
- **Avg Classification Consistency:** 87%
- **Accuracy:** 3/3 venues correctly classified

**Key Findings:**
1. Da Michele confirmed as highest variance (15 point spread)
2. Strong signals (explicit trap warnings OR local endorsement) reduce variance
3. Classification alignment is excellent despite score variance

**Full details:** See `docs/experiments/baseline_variance.md`

### Experiment 2: RAG Integration Impact

**Date:** [TO BE FILLED]
**Objective:** Measure variance reduction after RAG integration
**Method:** Same 5-run test on same venues with RAG enabled
**Hypothesis:** RAG examples will reduce variance by providing calibration anchors
**Comparison Metrics:**
- Variance reduction %
- Classification stability improvement
- Qualitative reasoning improvement

---

## Technical Decisions Log

### Decision 1: Pre-computed Metrics Architecture

**Date:** [Initial Development]
**Decision:** Compute quantitative signals (credibility, keywords, clustering) BEFORE LLM sees data
**Rationale:**
- Prevents LLM from being influenced by emotional review language
- Ensures consistent signal detection across runs
- Allows metrics to be independently validated
- Reduces token usage by summarizing instead of passing raw reviews

**Trade-offs:**
- (+) Consistent quantitative analysis
- (+) Auditable signal detection
- (-) May miss nuanced patterns LLM could catch in raw text
- (-) Keyword lists need manual maintenance

### Decision 2: Gemini 2.5 Flash vs Claude

**Date:** [Initial Development]
**Decision:** Use Google Gemini API
**Rationale:**
- Part of Google ecosystem (pairs with SerpAPI/Google Maps data)
- Structured JSON output via schema enforcement
- Cost-effective for project budget
- Fast response times for interactive UI

### Decision 3: RAG Database Strategy

**Date:** [RAG Development]
**Decision:** 149 curated examples, AI-generated via Gemini
**Rationale:**
- Sufficient diversity for few-shot retrieval
- Covers multiple categories (trap/gem/mixed)
- Global geographic coverage
- Includes embedding text for vector search

---

## Metrics Definitions

### Credibility Score (0-100)
- Base: 50 points
- +25: 100+ reviews (experienced_reviewer)
- +15: 20-99 reviews (moderate_reviewer)
- +5: 5-19 reviews
- -20: ≤3 reviews (new_account)
- +15: 50+ photos (photo_contributor)
- +10: 10-49 photos
- -10: 0 photos
- +20: Local Guide status

### Trap Signals
| Signal | Severity | Trigger |
|--------|----------|---------|
| credibility_inversion | high/medium | Negative reviewers 10+ points more credible |
| explicit_trap_warnings | high | 3+ reviews mention "tourist trap" etc. |
| manipulation_accusations | high | 2+ reviews claim fake/bought reviews |
| review_clustering | medium | 30%+ positive reviews on high-volume days |
| photo_credibility_gap | medium | Negative reviews 20%+ more likely to have photos |
| local_guide_warnings | medium | More Local Guides in negative than positive |
| service_food_disparity | medium | 2+ reviews rate service high but food low |

---

## RAG Database Overview

**File:** `RAG/rag_master.json`
**Total Entries:** 149
**Schema Version:** tourist_trap_rag_v1

### Distribution
```
Tourist Traps:    ~50 entries
Local Gems:       ~50 entries
Mixed:            ~49 entries
```

### Sample Entry Structure
```json
{
  "id": "unique-id",
  "name": "Venue Name",
  "location": "City, Country",
  "category": "restaurant|cafe|bar|attraction",
  "verdict": "tourist_trap|local_gem|mixed",
  "confidence": "high|medium|low",
  "tourist_trap_score": 0-100,
  "summary": "2-3 sentence description",
  "red_flags": [...],
  "positive_signals": [...],
  "sample_reviews": [...],
  "embedding_text": "Text used for vector similarity"
}
```

---

## UI/UX Notes

### Current Design
- Dark theme with orange accent (#f97316)
- Score visualization with color coding:
  - 0-20: Green (local gem)
  - 20-40: Lime (likely authentic)
  - 40-60: Yellow (unclear)
  - 60-80: Orange (likely trap)
  - 80-100: Red (definite trap)
- Tabbed interface: Signals, Concerns, Positives, Analysis
- Metrics grid showing key quantitative signals

### Planned Improvements
- [ ] Add RAG examples panel ("Similar venues analyzed")
- [ ] Show confidence intervals for scores
- [ ] Add "Re-analyze" button for variance testing
- [ ] Export full report as PDF

---

## Next Steps Checklist

- [ ] Run baseline variance experiment
- [ ] Implement RAG retrieval system
- [ ] Integrate RAG examples into prompt
- [ ] Run post-RAG variance experiment
- [ ] Analyze and document impact
- [ ] Optimize prompt engineering
- [ ] Final UI polish
- [ ] Prepare presentation

---

## Appendix: Useful Commands

```bash
# Activate environment
source venv/bin/activate

# Run web UI
python app.py

# Run CLI analysis
python main.py "Pizzeria Da Michele" "Naples"

# Run with mock data (no API key needed)
# Just ensure SERPAPI_KEY is not set in .env
```

---

## Session Log: 2024-12-14 - Methodology Improvements

### Overview

Implemented 4 key improvements to address methodology flaws identified during baseline testing, plus performance optimizations.

### Changes Made

#### 1. External Signals via Web Search (`src/tools/web_search.py`)

**New module** using Gemini 2.0 Flash Lite with Google Search grounding:

- `search_external_opinions()` - Searches Reddit, TripAdvisor forums, and food blogs for venue opinions
- `check_tourist_proximity()` - Determines if venue is in a tourist hotspot area

**Signals added:**
- `tourist_hotspot_location` (medium) - Venue in high-traffic tourist area
- `external_negative_reputation` (high) - Negative sentiment across external platforms

#### 2. Language Diversity Analysis (`src/metrics.py`)

Added language detection to identify tourist vs local reviewer patterns:

- `analyze_language_distribution()` - Detects language distribution using `langdetect`
- Analyzes positive and negative reviews separately

**Signal added:**
- `language_credibility_split` (high) - When tourists dominate positive reviews but locals dominate negative reviews

#### 3. Credible Positive Reviews in Prompt (`src/metrics.py`, `src/analyzer.py`)

Fixed confirmation bias by showing the LLM both sides:

- Extract top 3 credible positive reviews (sorted by credibility score)
- Include specificity score (0-100) measuring how detailed vs generic the review is
- `compute_specificity()` - Rewards specific ingredients, cooking methods, comparisons; penalizes generic praise

**Signal added:**
- `generic_positive_reviews` (medium) - When positive reviews lack specific details

#### 4. Performance Optimizations (`src/analyzer.py`)

- **Parallel API calls** - External signals fetched concurrently with `ThreadPoolExecutor`
- **Model downgrade** - Switched to `gemini-2.0-flash-lite` for both analysis and web search
- **Concise prompts** - Reduced `maxOutputTokens` and tightened response guidelines
- **Fewer reviews sent** - 5 negative, 3 positive (down from 8/5)

#### 5. UI Improvements (`app.py`)

- Added human-friendly signal name mapping (`SIGNAL_NAMES` dict)
- Signal names now display as "Credibility Inversion" instead of "credibility_inversion"

#### 6. Mock Data Cleanup (`src/tools/mock_data.py`, `src/tools/web_search.py`)

- Removed Hard Rock Cafe Rome from mock data
- Restored original 4 test venues: Da Michele, Olive Garden TS, Carlo Menta, Katz's
- Added mock web search and proximity data for all 4 venues

### Dependencies

- Added `langdetect>=1.0.9` to requirements.txt
- Removed `playwright` (unused optional dependency)

### Files Modified

| File | Changes |
|------|---------|
| `src/analyzer.py` | Parallel execution, flash-lite model, positive reviews in prompt |
| `src/metrics.py` | Language analysis, specificity scoring, credible positive reviews |
| `src/tools/web_search.py` | **NEW** - External signals + proximity via Gemini grounding |
| `src/tools/mock_data.py` | Removed Hard Rock, updated to 4 venues |
| `app.py` | Human-friendly signal names |
| `requirements.txt` | Added langdetect, removed playwright |

### Expected Impact

- **Speed:** ~2-3x faster inference with flash-lite model
- **Cost:** ~10x cheaper per analysis
- **Accuracy:** Better calibration with external signals and balanced review presentation
- **Consistency:** Language and specificity metrics provide additional anchoring

### Commit

```
Add web search signals, language analysis, and optimize inference speed
```

---

## Session Log: 2024-12-14 - Venue-Agnostic Support

### Overview

Implemented venue-agnostic analysis to support all venue types (restaurants, museums, attractions, tours, shops) instead of just restaurants.

### Problem Statement

The original implementation was restaurant-centric with hardcoded food/service keywords. This limited the system to restaurant analysis only, missing opportunities to detect tourist traps at museums, attractions, tours, and shops.

### Changes Made

#### 1. Venue Type Detection (`src/metrics.py`)

Added automatic venue type detection from Google Place types:

```python
VENUE_TYPE_RESTAURANT = "restaurant"
VENUE_TYPE_MUSEUM = "museum"
VENUE_TYPE_ATTRACTION = "attraction"
VENUE_TYPE_TOUR = "tour"
VENUE_TYPE_SHOP = "shop"
VENUE_TYPE_GENERAL = "general"
```

`infer_venue_type(place)` maps Google Place types to these categories:
- restaurant, cafe, bar, bakery → restaurant
- museum, art_gallery → museum
- tourist_attraction, amusement_park → attraction
- travel_agency → tour
- store, shopping_mall, market → shop

#### 2. Venue-Specific Keywords (`src/metrics.py`)

Added `QUALITY_KEYWORDS_BY_TYPE` with venue-specific complaint indicators:

| Venue Type | Example Keywords |
|------------|------------------|
| restaurant | cold food, overcooked, bland, stale |
| museum | crowded, confusing layout, poor audio |
| attraction | long lines, not worth it, photo op only |
| tour | rushed, large group, no knowledge |
| shop | overpriced, fake, pushy salespeople |

#### 3. Venue-Specific Specificity Indicators (`src/metrics.py`)

Added `SPECIFICITY_INDICATORS_BY_TYPE` for measuring review detail quality:

| Venue Type | Specificity Patterns |
|------------|---------------------|
| restaurant | ingredient names, cooking methods, dish comparisons |
| museum | exhibit names, artist names, collection details |
| attraction | specific features, historical facts, comparisons |
| tour | guide names, route details, timing specifics |
| shop | product names, price comparisons, quality details |

#### 4. Restaurant-Only Signals

Ensured `service_food_disparity` signal only fires for restaurants. Other venue types skip this check.

#### 5. External Search Updates (`src/tools/web_search.py`)

Added venue-specific source configuration:
- Restaurants: r/food, r/foodie, food blogs
- Museums: r/museums, r/ArtHistory, art blogs
- Attractions: r/travel, r/solotravel
- Tours: r/travel, tour review articles
- Shops: r/shopping, shopping guides

#### 6. RAG Retriever Updates (`src/rag/retriever.py`)

Added `venue_type` parameter to filter RAG examples by relevant categories:

```python
VENUE_TYPE_TO_RAG_CATEGORIES = {
    "restaurant": ["restaurant", "cafe", "bar", "street_food"],
    "museum": ["attraction", "museum"],
    "attraction": ["attraction", "museum"],
    "tour": ["attraction", "tour"],
    "shop": ["market", "shop"],
    "general": None,
}
```

### Files Modified

| File | Changes |
|------|---------|
| `src/metrics.py` | Added venue type constants, detection, keyword dictionaries, specificity patterns |
| `src/analyzer.py` | Added venue type detection call, passes venue_type through pipeline |
| `src/tools/web_search.py` | Added venue-specific source configuration |
| `src/rag/retriever.py` | Added venue_type parameter with category mapping |
| `CLAUDE.md` | Updated documentation with venue-agnostic details |

### RAG Database Coverage Analysis

Current RAG database category distribution:
- Restaurants: 55 entries (37%)
- Attractions: 39 entries (26%)
- Cafes: 15 entries (10%)
- Street Food: 13 entries (9%)
- Markets: 13 entries (9%)
- Bars: 11 entries (7%)
- Tours: 3 entries (2%)

**Gap identified:** Tours are underrepresented. May need additional tour examples for proper calibration.

### Testing

Verified venue type detection with test cases:
- "Pizzeria Da Michele" → restaurant ✓
- "Louvre Museum" → museum ✓
- "Vatican Tour" → tour ✓
- "Grand Bazaar" → shop ✓

### Commit

```
Add venue-agnostic support for museums, attractions, tours, and shops
```

---

*Last Updated: 2024-12-14*
