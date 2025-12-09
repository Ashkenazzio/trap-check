# Tourist Trap Detector - Project Initialization Prompt v2

## Project Context

You are helping me build a machine learning project for a 2-week university course on Applied Language Models. The project requirements include:
- RAG (Retrieval-Augmented Generation), LoRA-based fine-tuning, prompt-level optimization, OR Agentic AI workflows
- Can be implemented in Colab within two weeks using public datasets
- Must include: dataset/preprocessing, model/training OR pipeline setup, evaluation, and analysis

**We are pursuing an Agentic AI approach with RAG enhancement.**

---

## Project Overview

**Project Name:** Tourist Trap Detector

**Goal:** Build an agentic system that analyzes restaurants and venues to predict whether they are "tourist traps" — establishments that exploit tourist traffic with inflated prices, lower quality, and inauthentic experiences.

**User Experience Vision:**
The user provides EITHER:
1. A business name + location (e.g., "Pizzeria Da Michele, Naples")
2. A Google Maps URL (e.g., `https://maps.google.com/...`)

The system then:
1. **Automatically fetches** all relevant data (reviews, ratings, photos, metadata)
2. **Analyzes** the data using Claude API with RAG-enhanced context
3. **Returns a rich, evidence-based report** including:
   - Tourist trap probability score (0-100%)
   - Red flags with specific evidence (quoted reviews, screenshots)
   - Positive signals with evidence
   - Visual artifacts (screenshots of the Google Maps page, review highlights)
   - Comparative context (how it compares to similar venues)
   - Summary verdict with reasoning

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                    │
│  "Restaurant Name, City" OR Google Maps URL                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      AGENT ORCHESTRATOR (Claude API)                    │
│                                                                         │
│  Claude with tool-use capabilities orchestrates the entire flow:        │
│  1. Parse user input                                                    │
│  2. Call appropriate tools to gather data                               │
│  3. Retrieve relevant examples from RAG                                 │
│  4. Generate comprehensive analysis                                     │
│  5. Capture visual evidence                                             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
        ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
        │  DATA FETCHING   │ │  RAG SYSTEM  │ │ VISUAL CAPTURE   │
        │     TOOLS        │ │              │ │    (Playwright)  │
        ├──────────────────┤ ├──────────────┤ ├──────────────────┤
        │ • SerpAPI/       │ │ • ChromaDB   │ │ • Screenshot     │
        │   Outscraper     │ │ • Tourist    │ │   Google Maps    │
        │ • Google Maps    │ │   trap       │ │ • Capture review │
        │   search         │ │   examples   │ │   highlights     │
        │ • Review fetch   │ │ • Pattern    │ │ • Menu/price     │
        │   (paginated)    │ │   library    │ │   screenshots    │
        │ • Web search     │ │              │ │                  │
        │   (context)      │ │              │ │                  │
        └──────────────────┘ └──────────────┘ └──────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        RICH OUTPUT GENERATION                           │
│                                                                         │
│  Structured JSON + Visual Report with:                                  │
│  • Score gauge visualization                                            │
│  • Red flags with quoted evidence                                       │
│  • Embedded screenshots                                                 │
│  • Review excerpts with highlighting                                    │
│  • Confidence indicators                                                │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           WEB UI (Gradio)                               │
│                                                                         │
│  Beautiful, interactive interface displaying:                           │
│  • Input field for name/location or URL                                 │
│  • Loading state with progress                                          │
│  • Rich results panel with tabs/sections                                │
│  • Downloadable report                                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Critical Technical Constraints & Solutions

### 1. Google Maps API Review Limitation

**Problem:** Official Google Places API only returns 5 reviews maximum.

**Solutions (in order of preference):**

| Option | Pros | Cons | Cost |
|--------|------|------|------|
| **SerpAPI** | Reliable, paginated, structured JSON, good docs | Paid per search | ~$50/mo for 5000 searches |
| **Outscraper** | Unlimited reviews, free tier (500 reviews) | Slower, less structured | Free tier + $2/1000 reviews |
| **Apify** | $5/mo free credits (~10k reviews), good tooling | Learning curve | $0.5/1000 reviews |
| **Playwright scraping** | Free, full control | Fragile, may break, ToS risk | Free |

**Recommended approach:** 
- Use **SerpAPI** for reliable review fetching (they have a Google Maps Reviews API with pagination)
- Free tier: 100 searches/month — sufficient for development/demo
- Paid: $50/month for 5000 searches — reasonable for project scope

**SerpAPI Flow:**
```python
# 1. Search for the place
GET /search?engine=google_maps&q=restaurant+name+city

# 2. Get data_id from results
data_id = results['local_results'][0]['data_id']

# 3. Fetch reviews (paginated)
GET /search?engine=google_maps_reviews&data_id={data_id}

# 4. Paginate using next_page_token
GET /search?engine=google_maps_reviews&data_id={data_id}&next_page_token={token}
```

### 2. Screenshot Capture for Evidence

**Approach:** Use Playwright MCP or direct Playwright integration

**What to capture:**
1. Google Maps listing page (overall view)
2. Review panel (scrolled to show multiple reviews)
3. Photos section (if available)
4. Price/menu information (if available)

**Implementation:**
```python
from playwright.async_api import async_playwright

async def capture_google_maps_screenshot(place_url: str) -> bytes:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(place_url)
        await page.wait_for_selector('[data-review-id]')  # Wait for reviews to load
        screenshot = await page.screenshot(full_page=False)
        await browser.close()
        return screenshot
```

### 3. Review Data Limitations

**Typical data available per review:**
- `text` — Full review text
- `rating` — 1-5 stars
- `date` — When posted (relative, e.g., "2 months ago")
- `user.name` — Reviewer name
- `user.local_guide` — Whether they're a Local Guide
- `user.reviews` — How many reviews they've written
- `likes` — How many found this helpful

**What we CAN'T easily get:**
- Reviewer's home location (to classify as tourist vs local)
- Historical pricing data
- Comparative data within the same query

**Workarounds:**
- **Local Guide status** as proxy for "local" reviewer
- **Review count** as proxy for experienced reviewer
- **Web search** for additional context ("Is X a tourist trap reddit")

---

## Definition of "Tourist Trap"

For consistent analysis, the model should evaluate against these criteria:

### Red Flag Indicators (Negative Signals)

| Category | Specific Signals |
|----------|-----------------|
| **Price-Quality Mismatch** | "overpriced", "not worth it", "expensive for what you get", "ripoff", "tourist prices" |
| **Authenticity Issues** | "not authentic", "touristy", "Americanized", "fake", "Disney version", "nothing like the real thing" |
| **Local Avoidance** | "locals don't come here", "only tourists", "avoid", "stay away if you're local" |
| **Service Problems** | "rushed", "assembly line", "herded", "treated like cattle", "rude to non-tourists" |
| **Quality Decline** | "used to be good", "gone downhill", "not what it used to be", "sold out" |
| **Location Dependency** | "only good because of location", "you're paying for the view", "proximity tax" |
| **Review Manipulation** | Suspiciously similar reviews, sudden rating spikes, generic praise |

### Positive Indicators (Counter-Signals)

| Category | Specific Signals |
|----------|-----------------|
| **Local Endorsement** | "locals love it", "neighborhood gem", "where locals go", "my regular spot" |
| **Value Acknowledgment** | "worth every penny", "great value", "fair prices", "would pay more" |
| **Authenticity Praise** | "authentic", "traditional", "real deal", "just like in [origin country]" |
| **Repeat Visitors** | "come back every time", "10th visit", "annual tradition", "never disappoints" |
| **Specific Quality** | Detailed praise about specific dishes, ingredients, techniques |

### Contextual Factors

| Factor | Consideration |
|--------|---------------|
| **Price Tier** | A $$$ restaurant should deliver $$$ quality |
| **Location** | Near major attractions = higher scrutiny |
| **Category** | Some categories are more prone to traps (e.g., restaurants near Times Square) |
| **Review Volume** | Very high volume + generic reviews = suspicious |
| **Rating Distribution** | Natural distribution vs suspiciously polarized |

---

## Agent Tools Specification

### Tool 1: `search_place`
```json
{
  "name": "search_place",
  "description": "Search for a business on Google Maps by name and location",
  "parameters": {
    "query": "string - Business name",
    "location": "string - City, region, or country (optional)",
    "type": "string - Place type filter (optional): restaurant, cafe, bar, etc."
  },
  "returns": {
    "place_id": "string",
    "data_id": "string - Required for review fetching",
    "name": "string",
    "address": "string",
    "rating": "float",
    "review_count": "integer",
    "price_level": "string - $, $$, $$$, $$$$",
    "types": "array of strings",
    "gps_coordinates": "object with lat/lng",
    "google_maps_url": "string"
  }
}
```

### Tool 2: `fetch_reviews`
```json
{
  "name": "fetch_reviews",
  "description": "Fetch reviews for a place using its data_id. Supports pagination.",
  "parameters": {
    "data_id": "string - Google Maps data ID",
    "sort_by": "string - 'qualityScore' (default), 'newestFirst', 'ratingHigh', 'ratingLow'",
    "max_reviews": "integer - Maximum reviews to fetch (default: 50)",
    "language": "string - Filter by language code (optional)"
  },
  "returns": {
    "place_info": {
      "title": "string",
      "address": "string", 
      "rating": "float",
      "total_reviews": "integer"
    },
    "reviews": [
      {
        "text": "string",
        "rating": "integer 1-5",
        "date": "string",
        "user": {
          "name": "string",
          "local_guide": "boolean",
          "reviews_count": "integer"
        },
        "likes": "integer",
        "response": "string - Owner response if any"
      }
    ],
    "topics": [
      {
        "keyword": "string",
        "mentions": "integer"
      }
    ]
  }
}
```

### Tool 3: `web_search`
```json
{
  "name": "web_search",
  "description": "Search the web for additional context about a place",
  "parameters": {
    "query": "string - Search query"
  },
  "returns": {
    "results": [
      {
        "title": "string",
        "snippet": "string",
        "url": "string"
      }
    ]
  }
}
```

### Tool 4: `capture_screenshot`
```json
{
  "name": "capture_screenshot",
  "description": "Capture a screenshot of a Google Maps page or URL",
  "parameters": {
    "url": "string - URL to capture",
    "selector": "string - CSS selector to focus on (optional)",
    "full_page": "boolean - Capture full page or viewport only"
  },
  "returns": {
    "image_base64": "string",
    "image_url": "string - Temporary URL to the image"
  }
}
```

### Tool 5: `retrieve_similar_examples`
```json
{
  "name": "retrieve_similar_examples",
  "description": "Retrieve similar tourist trap/gem examples from the RAG database for few-shot context",
  "parameters": {
    "query": "string - Description or category to match",
    "category": "string - 'tourist_trap', 'local_gem', 'mixed'",
    "limit": "integer - Number of examples to retrieve (default: 3)"
  },
  "returns": {
    "examples": [
      {
        "name": "string",
        "location": "string",
        "verdict": "string - 'tourist_trap' or 'local_gem'",
        "summary": "string",
        "key_signals": ["string"]
      }
    ]
  }
}
```

---

## RAG Database Schema

### Collection: `tourist_trap_examples`

**Purpose:** Store labeled examples of known tourist traps and quality establishments for few-shot retrieval.

**Document Schema:**
```json
{
  "id": "string",
  "name": "string",
  "location": "string",
  "category": "string - restaurant, cafe, attraction, etc.",
  "verdict": "string - 'tourist_trap' | 'local_gem' | 'mixed'",
  "confidence": "string - 'high' | 'medium' | 'low'",
  "tourist_trap_score": "integer 0-100",
  "summary": "string - 2-3 sentence summary",
  "red_flags": [
    {
      "type": "string",
      "description": "string",
      "evidence": "string - quote or example"
    }
  ],
  "positive_signals": [
    {
      "type": "string", 
      "description": "string",
      "evidence": "string"
    }
  ],
  "sample_reviews": [
    {
      "text": "string",
      "rating": "integer",
      "is_tourist": "boolean - if determinable",
      "highlights": ["string - key phrases"]
    }
  ],
  "metadata": {
    "source": "string",
    "date_added": "datetime",
    "verified": "boolean"
  },
  "embedding": "vector - for similarity search"
}
```

### Building the RAG Database

**Initial Data Sources:**
1. **Curated list of known tourist traps** — Research online (Reddit, travel forums, articles like "tourist traps to avoid in [city]")
2. **Curated list of local gems** — "Where locals eat in [city]", "hidden gems [city]"
3. **Manually labeled examples** — 50-100 examples with clear verdicts

**Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (fast, good quality)

**Vector Store:** ChromaDB (simple, local, good for project scope)

```python
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize
client = chromadb.Client()
collection = client.create_collection("tourist_trap_examples")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Add document
def add_example(doc):
    text_to_embed = f"{doc['name']} {doc['location']} {doc['summary']} {' '.join([f['description'] for f in doc['red_flags']])}"
    embedding = embedder.encode(text_to_embed).tolist()
    collection.add(
        ids=[doc['id']],
        embeddings=[embedding],
        documents=[json.dumps(doc)],
        metadatas=[{"verdict": doc['verdict'], "category": doc['category']}]
    )

# Query for similar
def retrieve_similar(query, verdict_filter=None, n=3):
    query_embedding = embedder.encode(query).tolist()
    where_filter = {"verdict": verdict_filter} if verdict_filter else None
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        where=where_filter
    )
    return [json.loads(doc) for doc in results['documents'][0]]
```

---

## Output Schema

### Analysis Response Structure

```json
{
  "meta": {
    "query": "string - Original user input",
    "place_name": "string",
    "place_address": "string",
    "analysis_timestamp": "datetime",
    "data_sources": ["reviews", "web_search", "screenshots"],
    "reviews_analyzed": "integer"
  },
  
  "verdict": {
    "tourist_trap_score": "integer 0-100",
    "confidence": "string - 'high' | 'medium' | 'low'",
    "classification": "string - 'likely_trap' | 'possibly_trap' | 'neutral' | 'likely_gem' | 'local_favorite'",
    "one_liner": "string - Single sentence summary"
  },
  
  "evidence": {
    "red_flags": [
      {
        "type": "string - e.g., 'price_quality_mismatch'",
        "severity": "string - 'high' | 'medium' | 'low'",
        "description": "string",
        "supporting_quotes": [
          {
            "text": "string - Exact quote from review",
            "source": "string - Review author",
            "rating": "integer",
            "date": "string"
          }
        ],
        "frequency": "string - 'mentioned often' | 'occasional' | 'rare'"
      }
    ],
    "positive_signals": [
      {
        "type": "string",
        "strength": "string - 'strong' | 'moderate' | 'weak'",
        "description": "string",
        "supporting_quotes": [...]
      }
    ],
    "notable_patterns": [
      {
        "pattern": "string",
        "description": "string"
      }
    ]
  },
  
  "context": {
    "location_risk": "string - How tourist-heavy is the area",
    "category_risk": "string - How common are traps in this category",
    "price_tier": "string",
    "comparable_alternatives": [
      {
        "name": "string",
        "why_better": "string"
      }
    ]
  },
  
  "visuals": {
    "main_screenshot": "string - base64 or URL",
    "review_highlights": ["string - URLs to highlighted screenshots"],
    "rating_distribution_chart": "string - base64 of chart"
  },
  
  "detailed_reasoning": "string - 2-3 paragraph explanation of the analysis"
}
```

---

## Web UI Specification (Gradio)

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│  🎯 TOURIST TRAP DETECTOR                                           │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Enter restaurant name & city, or paste Google Maps URL:    │   │
│  │  [___________________________________________________]      │   │
│  │                                              [🔍 Analyze]   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────────┐  ┌────────────────────────────────────┐  │
│  │                      │  │  📊 VERDICT                        │  │
│  │   [SCREENSHOT]       │  │  ────────────────────────────────  │  │
│  │   Google Maps        │  │                                    │  │
│  │   Preview            │  │  Tourist Trap Score: [====75%===]  │  │
│  │                      │  │  Confidence: HIGH                  │  │
│  │                      │  │                                    │  │
│  │                      │  │  ⚠️ LIKELY TOURIST TRAP            │  │
│  │                      │  │                                    │  │
│  └──────────────────────┘  │  "This restaurant shows classic    │  │
│                            │   tourist trap patterns..."         │  │
│                            └────────────────────────────────────┘  │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  [🚩 Red Flags] [✅ Positive] [📝 Reviews] [📸 Evidence]    │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                             │   │
│  │  🚩 RED FLAG: Price-Quality Mismatch (HIGH severity)        │   │
│  │  ───────────────────────────────────────────────────────    │   │
│  │  Multiple reviewers mention overpriced food...              │   │
│  │                                                             │   │
│  │  📌 "Paid €40 for a pizza that was mediocre at best..."    │   │
│  │     — Marco R. ⭐⭐ (2 months ago)                          │   │
│  │                                                             │   │
│  │  📌 "Tourist trap prices. Same pizza costs half..."         │   │
│  │     — Local Guide Sarah ⭐⭐⭐ (1 month ago)                 │   │
│  │                                                             │   │
│  │  [See 4 more quotes...]                                     │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  [📥 Download Full Report (PDF)]  [🔗 Share Analysis]       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Gradio Implementation Skeleton

```python
import gradio as gr

def analyze_venue(input_text: str, progress=gr.Progress()) -> dict:
    """Main analysis function"""
    progress(0.1, desc="Parsing input...")
    # Parse input (name+location or URL)
    
    progress(0.2, desc="Searching for venue...")
    # Call search_place tool
    
    progress(0.4, desc="Fetching reviews...")
    # Call fetch_reviews tool (may take time)
    
    progress(0.6, desc="Capturing screenshots...")
    # Call capture_screenshot tool
    
    progress(0.7, desc="Searching for additional context...")
    # Call web_search tool
    
    progress(0.8, desc="Retrieving similar examples...")
    # Call retrieve_similar_examples tool
    
    progress(0.9, desc="Analyzing with AI...")
    # Send everything to Claude for analysis
    
    progress(1.0, desc="Generating report...")
    # Format and return results
    
    return analysis_result

# Build UI
with gr.Blocks(theme=gr.themes.Soft(), title="Tourist Trap Detector") as demo:
    gr.Markdown("# 🎯 Tourist Trap Detector")
    gr.Markdown("*Find out if that restaurant is worth your money, or just another tourist trap.*")
    
    with gr.Row():
        input_box = gr.Textbox(
            label="Enter restaurant name & city, or paste Google Maps URL",
            placeholder="e.g., 'Pizzeria Da Michele, Naples' or Google Maps link...",
            lines=1
        )
        analyze_btn = gr.Button("🔍 Analyze", variant="primary")
    
    with gr.Row():
        with gr.Column(scale=1):
            screenshot_display = gr.Image(label="Google Maps Preview")
        
        with gr.Column(scale=2):
            with gr.Group():
                gr.Markdown("### 📊 Verdict")
                score_display = gr.Slider(
                    label="Tourist Trap Score",
                    minimum=0, maximum=100,
                    interactive=False
                )
                confidence_display = gr.Textbox(label="Confidence", interactive=False)
                verdict_display = gr.Markdown()
    
    with gr.Tabs():
        with gr.Tab("🚩 Red Flags"):
            red_flags_display = gr.Markdown()
        
        with gr.Tab("✅ Positive Signals"):
            positive_signals_display = gr.Markdown()
        
        with gr.Tab("📝 Review Analysis"):
            reviews_display = gr.Markdown()
        
        with gr.Tab("📸 Evidence"):
            evidence_gallery = gr.Gallery(label="Screenshots & Evidence")
    
    reasoning_display = gr.Markdown(label="Detailed Analysis")
    
    with gr.Row():
        download_btn = gr.Button("📥 Download Report")
        share_btn = gr.Button("🔗 Share")
    
    # Connect events
    analyze_btn.click(
        fn=analyze_venue,
        inputs=[input_box],
        outputs=[screenshot_display, score_display, confidence_display, 
                 verdict_display, red_flags_display, positive_signals_display,
                 reviews_display, evidence_gallery, reasoning_display]
    )

demo.launch()
```

---

## Project Implementation Checklist

### Phase 1: Infrastructure Setup (Days 1-2)
- [ ] Set up SerpAPI account and get API key
- [ ] Set up Anthropic API access (Claude)
- [ ] Create Colab notebook with required dependencies
- [ ] Test basic API connectivity

### Phase 2: Data Fetching Tools (Days 3-4)
- [ ] Implement `search_place` tool wrapper
- [ ] Implement `fetch_reviews` tool with pagination
- [ ] Implement `web_search` tool
- [ ] Implement `capture_screenshot` with Playwright
- [ ] Test each tool independently

### Phase 3: RAG System (Days 5-6)
- [ ] Research and curate 50-100 labeled examples
- [ ] Set up ChromaDB vector store
- [ ] Implement embedding and retrieval
- [ ] Implement `retrieve_similar_examples` tool
- [ ] Test retrieval quality

### Phase 4: Agent Integration (Days 7-8)
- [ ] Design Claude system prompt with tool definitions
- [ ] Implement tool-calling loop
- [ ] Test end-to-end flow
- [ ] Refine prompts based on output quality

### Phase 5: Web UI (Days 9-10)
- [ ] Build Gradio interface skeleton
- [ ] Implement progress tracking
- [ ] Add all display components
- [ ] Style and polish UI
- [ ] Add download/export functionality

### Phase 6: Evaluation & Documentation (Days 11-12)
- [ ] Create test set of 20-30 known venues
- [ ] Run evaluations and compute metrics
- [ ] Document failure cases
- [ ] Write project report
- [ ] Create presentation slides

### Phase 7: Polish & Demo (Days 13-14)
- [ ] Fix bugs found in testing
- [ ] Optimize performance
- [ ] Record demo video
- [ ] Final presentation prep

---

## Evaluation Framework

### Quantitative Metrics

**Test Set Construction:**
- 10 known tourist traps (researched, confirmed)
- 10 known local gems (researched, confirmed)
- 10 ambiguous/borderline cases

**Metrics:**
- **Accuracy:** Correct classification rate on binary trap/not-trap
- **Precision/Recall:** For tourist trap detection specifically
- **Calibration:** How well does the 0-100 score correlate with ground truth?
- **Evidence Quality:** Human evaluation of supporting quotes (relevant? convincing?)

### Qualitative Evaluation

For each test case, evaluate:
1. Is the verdict reasonable?
2. Are the red flags actually concerning?
3. Are the supporting quotes relevant?
4. Is the reasoning coherent?
5. Would this help a real user make a decision?

### Baseline Comparisons

1. **Zero-shot Claude:** Same prompt but without RAG examples
2. **Keyword matching:** Simple rules based on word presence
3. **Rating threshold:** Just use Google rating (< 4.0 = trap)

---

## API Cost Estimates

### Per-Query Costs (Single Venue Analysis)

| Component | API Calls | Cost |
|-----------|-----------|------|
| SerpAPI - Place Search | 1 | ~$0.01 |
| SerpAPI - Reviews (50 reviews, ~3 pages) | 3 | ~$0.03 |
| Claude Sonnet - Analysis (~4k tokens in, ~2k out) | 1 | ~$0.02 |
| **Total per query** | | **~$0.06** |

### Project Budget

| Phase | Estimated Usage | Cost |
|-------|-----------------|------|
| Development & Testing | ~200 queries | ~$12 |
| RAG Database Building | ~100 queries | ~$6 |
| Evaluation | ~50 queries | ~$3 |
| Demo/Presentation | ~20 queries | ~$1.20 |
| **Total** | | **~$22** |

This is well within reasonable project budgets.

---

## Known Limitations & Mitigations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| Can't determine reviewer's home location | Can't definitively classify tourist vs local | Use Local Guide status and review count as proxies |
| SerpAPI may not have all reviews | Some very new reviews might be missing | Note review freshness in output |
| Screenshots may break with Google UI changes | Visual evidence could fail | Graceful fallback to text-only evidence |
| Subjective ground truth | Hard to definitively label some venues | Use confidence levels, present nuanced verdicts |
| Non-English reviews | May miss signals in local language | Use language filter, or translate key reviews |
| API rate limits | Could slow down batch testing | Implement caching, respect rate limits |

---

## Questions to Resolve During Development

1. **SerpAPI vs Outscraper:** Test both and choose based on reliability and cost
2. **Screenshot approach:** Playwright locally vs cloud service (Browserless)?
3. **RAG example count:** How many examples provide optimal few-shot context?
4. **Review count:** Is 50 reviews sufficient, or do we need more for accuracy?
5. **Caching strategy:** Cache venue data for how long?

---

## How to Use This Prompt

When working on this project, reference this document and ask:

- "Help me implement the SerpAPI integration for fetching reviews"
- "Design the Claude system prompt for the agent"
- "Build the Gradio UI component for displaying red flags"
- "Create the RAG database seeding script"
- "Help me evaluate the model on the test set"

The AI assistant will have full context of the architecture, constraints, and goals.

---

## Resources & Links

- **SerpAPI Docs:** https://serpapi.com/google-maps-reviews-api
- **Outscraper Docs:** https://outscraper.com/google-maps-reviews-api/
- **Anthropic Claude API:** https://docs.anthropic.com/
- **Gradio Docs:** https://www.gradio.app/docs
- **ChromaDB Docs:** https://docs.trychroma.com/
- **Playwright Python:** https://playwright.dev/python/
