# RAG Database Collection Prompts

This document contains phased prompts for instructing an LLM to collect labeled examples for the Tourist Trap Detector RAG database.

## Overview

| Phase | Purpose | Output |
|-------|---------|--------|
| **Phase 1** | Generate balanced candidate list | ~150 venue names with basic classification |
| **Phase 2** | Review distribution, fill gaps, remove weak entries | Refined candidate list ready for research |
| **Phase 3** | Collect detailed evidence for each venue | Full evidence with quotes and sources |
| **Phase 4** | Format into final schema with embedding text | Production-ready JSON |
| **Phase 5** | Verify quality, consistency, catch fabrications | Verification report + fixes |

## Dataset Size Recommendation

**Target: 150 examples** — enough for good coverage without excessive curation burden.

| Size | Use Case | Tradeoffs |
|------|----------|-----------|
| 50-100 | Few-shot retrieval (3-5 examples per query) | Faster to curate, may lack coverage of edge cases |
| 150-200 | Better coverage of cities, categories, edge cases | More work, but stronger pattern matching |
| 200+ | Diminishing returns for RAG; better for fine-tuning | Overkill for retrieval-only |

---

## Phase 1: Candidate List Generation

```
# Phase 1: Tourist Trap RAG Database — Candidate List Generation

## Task
Generate a comprehensive list of **150 candidate venues** for a tourist trap detection dataset. This is a PLANNING phase — you are only collecting names and basic classification, NOT detailed evidence yet.

## Requirements

### Geographic Distribution (aim for global coverage)
Target **20-25 cities** across these regions:

| Region | Cities (pick 4-6 per region) | Target Venues |
|--------|------------------------------|---------------|
| **Western Europe** | Rome, Venice, Florence, Paris, Barcelona, Amsterdam, Prague, London, Vienna, Lisbon | 35-40 |
| **North America** | New York, Las Vegas, San Francisco, New Orleans, Miami, Los Angeles, Cancun | 30-35 |
| **Asia** | Bangkok, Tokyo, Kyoto, Bali, Hong Kong, Singapore, Hanoi, Beijing | 30-35 |
| **Other Tourist Hotspots** | Dubai, Sydney, Rio de Janeiro, Marrakech, Reykjavik, Santorini | 20-25 |
| **Emerging/Underrepresented** | Mexico City, Istanbul, Cape Town, Buenos Aires, Lisbon, Dubrovnik | 15-20 |

### Category Distribution

| Category | Percentage | Count (~150 total) |
|----------|------------|---------------------|
| Restaurants | 55-60% | 82-90 |
| Cafes & Bars | 15-20% | 22-30 |
| Street Food & Markets | 10-15% | 15-22 |
| Attractions & Tours | 8-12% | 12-18 |

### Verdict Distribution

| Verdict | Percentage | Count |
|---------|------------|-------|
| **tourist_trap** | 40-45% | 60-68 |
| **local_gem** | 40-45% | 60-68 |
| **mixed** | 10-15% | 15-22 |

### Price Tier Distribution (within each verdict)
- Budget ($): 25-30%
- Mid-range ($$): 40-50%
- Upscale ($$$): 20-25%
- Luxury ($$$$): 5-10%

---

## Research Approach

For each city, search for:

**To find Tourist Traps:**
- "[city] tourist traps to avoid"
- "[city] overrated restaurants reddit"
- "[city] restaurants locals avoid"
- "worst restaurants near [landmark]"
- "[city] food scams"

**To find Local Gems:**
- "where locals eat in [city]"
- "[city] hidden gems reddit"
- "[city] best restaurants locals"
- "authentic [cuisine] in [city]"
- "[city] neighborhood restaurants"

**To find Mixed/Borderline:**
- "[city] worth it despite tourists"
- "famous [city] restaurants actually good"
- "[city] overrated but still worth visiting"

---

## Output Format

Return a structured list with basic information only:

{
  "phase": "candidate_list",
  "generation_date": "YYYY-MM-DD",
  "target_count": 150,
  "actual_count": <number>,

  "distribution_summary": {
    "by_verdict": {"tourist_trap": X, "local_gem": Y, "mixed": Z},
    "by_region": {"western_europe": X, "north_america": Y, ...},
    "by_category": {"restaurant": X, "cafe": Y, ...}
  },

  "candidates": [
    {
      "id": 1,
      "name": "Exact Venue Name",
      "city": "City",
      "country": "Country",
      "category": "restaurant | cafe | bar | street_food | market | attraction | tour",
      "preliminary_verdict": "tourist_trap | local_gem | mixed",
      "price_tier": "$ | $$ | $$$ | $$$$",
      "fame_level": "iconic | well_known | moderate | under_radar",
      "primary_reason": "One sentence on why this classification",
      "source_hint": "Where you found this (e.g., 'r/rome, multiple threads')"
    }
  ]
}

---

## Quality Criteria for Inclusion

### INCLUDE venues that:
- Are mentioned in **multiple independent sources** with consistent sentiment
- Have **clear, documentable** reasons for their classification
- Represent **diverse price points** (not just expensive = trap)
- Include some **surprising entries** (famous places that are actually good, or hidden traps)

### EXCLUDE venues that:
- Have highly **mixed/contradictory** opinions with no consensus
- Are too **obscure** to find reliable information about
- Are **chains** (McDonald's, Starbucks) — focus on unique establishments
- Have **closed permanently**

---

## Example Output Entries

{
  "id": 1,
  "name": "Caffè Florian",
  "city": "Venice",
  "country": "Italy",
  "category": "cafe",
  "preliminary_verdict": "tourist_trap",
  "price_tier": "$$$$",
  "fame_level": "iconic",
  "primary_reason": "Consistently cited for €15+ coffees; universally acknowledged as paying for location not quality",
  "source_hint": "r/travel, TripAdvisor forums, multiple travel blogs"
}

{
  "id": 2,
  "name": "Da Enzo al 29",
  "city": "Rome",
  "country": "Italy",
  "category": "restaurant",
  "preliminary_verdict": "local_gem",
  "price_tier": "$$",
  "fame_level": "well_known",
  "primary_reason": "Repeatedly mentioned as 'where Romans actually eat' with exceptional cacio e pepe",
  "source_hint": "Eater Rome, r/rome, food blogs"
}

{
  "id": 3,
  "name": "Katz's Delicatessen",
  "city": "New York",
  "country": "USA",
  "category": "restaurant",
  "preliminary_verdict": "mixed",
  "price_tier": "$$$",
  "fame_level": "iconic",
  "primary_reason": "Famous and touristy, but food quality consistently praised even by locals; worth it despite crowds",
  "source_hint": "r/nyc, Serious Eats, multiple sources"
}

---

## Deliverable Checklist

Before submitting, verify:
- [ ] Total count is 145-155 venues
- [ ] All 5 regions represented with reasonable distribution
- [ ] tourist_trap and local_gem each have 40-45% representation
- [ ] mixed category has 10-15%
- [ ] At least 4 categories represented
- [ ] Price tiers are varied (not just expensive places)
- [ ] No duplicate venues
- [ ] Each entry has a clear primary_reason

---

## Begin

Generate the candidate list now. Prioritize **diversity and balance** over hitting exact numbers. It's better to have 140 well-chosen candidates than 150 with padding.
```

---

## Phase 2: Review & Refine Candidate List

```
# Phase 2: Tourist Trap RAG Database — Candidate List Review

## Context
You previously generated a candidate list of ~150 venues for a tourist trap detection RAG database. Now we need to review and refine this list before collecting detailed evidence.

## Input
[INSERT PHASE 1 OUTPUT HERE]

---

## Review Tasks

### Task 2.1: Distribution Analysis
Analyze the current distribution and identify gaps:

Current distribution:
- By verdict: [calculate from input]
- By region: [calculate from input]
- By category: [calculate from input]
- By price tier: [calculate from input]

Flag any categories with:
- Less than 35% or more than 50% for tourist_trap/local_gem
- Any region with less than 10% representation
- Restaurants below 50% or above 65%
- Any price tier below 15% representation

### Task 2.2: Duplicate & Conflict Check
Identify:
- Duplicate entries (same venue listed twice)
- Same venue in different locations (chain that shouldn't be included)
- Entries where the preliminary verdict seems questionable based on your knowledge

### Task 2.3: Gap Filling
Based on the distribution analysis, suggest **specific additions** to fill gaps:
- If a region is underrepresented, suggest 5-10 specific venues
- If a category is underrepresented, suggest specific venues
- If mixed verdicts are under 10%, identify borderline cases to add

### Task 2.4: Quality Filtering
Flag entries that should be **removed or reconsidered**:
- Venues that may have closed
- Venues with insufficient online presence to gather evidence
- Venues where classification is too controversial/uncertain
- Entries that seem like padding rather than genuine examples

---

## Output Format

{
  "phase": "candidate_review",
  "review_date": "YYYY-MM-DD",

  "distribution_analysis": {
    "current_totals": {
      "total": X,
      "by_verdict": {...},
      "by_region": {...},
      "by_category": {...},
      "by_price_tier": {...}
    },
    "gaps_identified": [
      "Gap description 1",
      "Gap description 2"
    ],
    "balance_score": "good | acceptable | needs_work"
  },

  "flagged_for_removal": [
    {
      "id": X,
      "name": "Venue name",
      "reason": "Why it should be removed"
    }
  ],

  "flagged_for_reconsideration": [
    {
      "id": X,
      "name": "Venue name",
      "current_verdict": "tourist_trap",
      "suggested_verdict": "mixed",
      "reason": "Why the classification might be wrong"
    }
  ],

  "suggested_additions": [
    {
      "name": "New venue name",
      "city": "City",
      "country": "Country",
      "category": "category",
      "preliminary_verdict": "verdict",
      "price_tier": "tier",
      "fills_gap": "What gap this fills"
    }
  ],

  "final_recommendations": {
    "remove_count": X,
    "reconsider_count": X,
    "add_count": X,
    "projected_final_count": X
  }
}

---

## Decision Criteria

### Remove if:
- Cannot find venue on Google Maps
- Primarily mentioned in only 1 source
- Classification requires significant local context unavailable online
- Is a chain or franchise

### Reconsider verdict if:
- Sources show 60/40 split in sentiment (should likely be "mixed")
- Evidence for current verdict is weak
- Your research contradicts the preliminary classification

### Add if:
- Fills a clear gap in distribution
- Is a well-documented example you're confident about
- Adds diversity to the dataset

---

## Deliverable

After completing this review, provide:
1. The analysis output above
2. A **FINAL CANDIDATE LIST** incorporating all changes
   - Remove flagged entries
   - Update reconsidered verdicts
   - Add new entries

The final list should be ready for Phase 3 (evidence collection).
```

---

## Phase 3: Evidence Collection

```
# Phase 3: Tourist Trap RAG Database — Evidence Collection

## Context
You have a reviewed candidate list of ~150 venues. Now collect detailed evidence for each venue to build the full RAG database entries.

## Input
[INSERT FINAL CANDIDATE LIST FROM PHASE 2]

---

## Evidence Collection Protocol

For EACH venue in the candidate list, collect:

### 3.1 Red Flags (for ALL venues, even gems)
Search for negative signals using these queries:
- "[venue name] overpriced"
- "[venue name] tourist trap"
- "[venue name] avoid"
- "[venue name] not worth it"
- "[venue name] review" (look for 1-2 star reviews)

Categorize findings into these types:

| Type | What to Look For |
|------|------------------|
| price_quality_mismatch | Complaints about value, "not worth the money" |
| authenticity_issues | "Not authentic", "touristy", "Americanized" |
| local_avoidance | "Locals don't come here", "only tourists" |
| service_problems | "Rushed", "rude", "didn't care" |
| quality_decline | "Used to be good", "gone downhill" |
| location_dependency | "Paying for the view", "only because of location" |
| review_manipulation | "Fake reviews", suspicious patterns |

### 3.2 Positive Signals (for ALL venues, even traps)
Search for positive signals:
- "[venue name] worth it"
- "[venue name] hidden gem"
- "[venue name] locals"
- "[venue name] best [dish/item]"
- "[venue name] review" (look for 4-5 star reviews)

Categorize findings into these types:

| Type | What to Look For |
|------|------------------|
| local_endorsement | "Where locals go", "neighborhood favorite" |
| value_acknowledgment | "Worth every penny", "great value" |
| authenticity_praise | "Authentic", "traditional", "real deal" |
| repeat_visitors | "Come back every time", "annual tradition" |
| specific_quality | Detailed praise about specific items |

### 3.3 Sample Reviews
Collect 2-4 representative reviews per venue:
- At least 1 negative (if available)
- At least 1 positive (if available)
- Try to include reviews from identifiable locals vs tourists
- Capture the EXACT quote or close paraphrase

### 3.4 Source Documentation
For each piece of evidence, note:
- Source (Reddit thread, TripAdvisor, blog name, Google Maps)
- Approximate date if visible
- Whether the reviewer appears to be local or tourist

---

## Output Schema

For each venue, produce this structure:

{
  "id": "slug-venue-name-city",
  "name": "Exact Venue Name",
  "location": "City, Country",
  "category": "restaurant | cafe | bar | street_food | market | attraction | tour",
  "verdict": "tourist_trap | local_gem | mixed",
  "confidence": "high | medium | low",
  "tourist_trap_score": 0-100,

  "summary": "2-3 sentence summary synthesizing the evidence. Explain WHY this venue earned its verdict.",

  "red_flags": [
    {
      "type": "price_quality_mismatch",
      "description": "Clear description of the issue",
      "evidence": "Direct quote or specific observation with source"
    }
  ],

  "positive_signals": [
    {
      "type": "local_endorsement",
      "description": "Clear description of the positive",
      "evidence": "Direct quote or specific observation with source"
    }
  ],

  "sample_reviews": [
    {
      "text": "Exact or closely paraphrased review text",
      "rating": 1-5,
      "is_local": true | false | null,
      "source": "Google Maps | TripAdvisor | Reddit | Yelp",
      "highlights": ["key phrase 1", "key phrase 2"]
    }
  ],

  "metadata": {
    "sources": ["List of all sources consulted"],
    "date_collected": "YYYY-MM-DD",
    "verification_notes": "Any notes about confidence in the classification"
  }
}

---

## Scoring Guidelines

### tourist_trap_score Assignment:

| Score Range | Criteria |
|-------------|----------|
| 85-100 | Overwhelming negative consensus, multiple severe red flags, virtually no defenders |
| 70-84 | Clear tourist trap with strong evidence, minor redeeming qualities |
| 55-69 | More trap than gem, but some legitimate positive aspects |
| 45-54 | True mixed case, roughly equal evidence both ways |
| 30-44 | More gem than trap, but has notable issues |
| 15-29 | Clear local gem with strong evidence, minor criticisms |
| 0-14 | Universally praised, no significant red flags |

### confidence Assignment:

| Level | Criteria |
|-------|----------|
| high | 5+ independent sources agree, clear evidence, no significant contradictions |
| medium | 3-4 sources, mostly consistent, some minor contradictions |
| low | Limited sources, or significant contradictions in evidence |

---

## Quality Requirements

For each venue entry:
- [ ] At least 2 red_flags OR explanation why none exist
- [ ] At least 2 positive_signals OR explanation why none exist
- [ ] At least 2 sample_reviews from different sources
- [ ] Summary accurately reflects the evidence
- [ ] Score is justified by the evidence
- [ ] All quotes are real (not fabricated)

---

## Batch Processing

Process venues in batches of 20-25 to maintain quality. After each batch:
1. Review for consistency in scoring
2. Check that similar venues have similar scores
3. Verify no evidence was fabricated

---

## Begin

Start collecting evidence for the first batch of venues. Prioritize accuracy over speed — fabricated evidence will poison the RAG database.
```

---

## Phase 4: Structured Data Formatting

```
# Phase 4: Tourist Trap RAG Database — Data Structuring & Formatting

## Context
You have collected evidence for ~150 venues. Now format everything into the final structured database ready for ChromaDB ingestion.

## Input
[INSERT PHASE 3 EVIDENCE COLLECTION OUTPUT]

---

## Formatting Tasks

### Task 4.1: ID Normalization
Ensure all IDs follow this format:
- Pattern: {category}-{venue-name-slug}-{city-slug}
- Lowercase, hyphens only, no special characters
- Example: restaurant-da-enzo-al-29-rome

### Task 4.2: Text Normalization
For each text field:
- Fix encoding issues (smart quotes → regular quotes)
- Standardize currency symbols (€, $, £)
- Remove excessive whitespace
- Ensure consistent capitalization in names

### Task 4.3: Category Standardization
Map all categories to exactly one of:
- restaurant
- cafe
- bar
- street_food
- market
- attraction
- tour

### Task 4.4: Embedding Text Generation
For each entry, generate the embedding_text field that will be used for similarity search:

Format:
{name} in {location}. {category}. {verdict}. {summary} Red flags: {comma-separated red flag descriptions}. Positives: {comma-separated positive descriptions}.

Example:
Caffè Florian in Venice, Italy. cafe. tourist_trap. Historic cafe with €15 coffees, paying for St. Mark's Square location rather than quality. Red flags: extreme overpricing, location-dependent value, tourist-only clientele. Positives: historic atmosphere, beautiful interior, bucket-list experience.

---

## Final Output Schema

{
  "database_metadata": {
    "version": "1.0",
    "created_date": "YYYY-MM-DD",
    "total_entries": 150,
    "schema_version": "tourist_trap_rag_v1",
    "distribution": {
      "by_verdict": {"tourist_trap": X, "local_gem": Y, "mixed": Z},
      "by_region": {...},
      "by_category": {...},
      "by_confidence": {"high": X, "medium": Y, "low": Z}
    }
  },

  "entries": [
    {
      "id": "restaurant-caffe-florian-venice",
      "name": "Caffè Florian",
      "location": "Venice, Italy",
      "city": "Venice",
      "country": "Italy",
      "region": "western_europe",
      "category": "cafe",
      "verdict": "tourist_trap",
      "confidence": "high",
      "tourist_trap_score": 85,
      "price_tier": "$$$$",

      "summary": "Historic cafe in St. Mark's Square charging €15+ for a coffee...",

      "red_flags": [
        {
          "type": "price_quality_mismatch",
          "description": "Coffee prices 5-10x normal Venice prices for standard quality",
          "evidence": "\"€15 for an espresso that would cost €1.50 elsewhere\" - TripAdvisor review",
          "severity": "high"
        }
      ],

      "positive_signals": [
        {
          "type": "specific_quality",
          "description": "Historic atmosphere and beautiful interior",
          "evidence": "\"The oldest cafe in Italy, stunning frescoes\" - Google Maps review",
          "strength": "moderate"
        }
      ],

      "sample_reviews": [
        {
          "text": "Paid €45 for two coffees and a small pastry...",
          "rating": 2,
          "is_local": false,
          "source": "TripAdvisor",
          "highlights": ["nothing special", "paying for history"]
        }
      ],

      "metadata": {
        "sources": ["Reddit r/travel", "TripAdvisor Venice forum", "Google Maps reviews"],
        "date_collected": "2024-01-15",
        "verification_notes": "Consistent across 50+ reviews mentioning overpricing."
      },

      "embedding_text": "Caffè Florian in Venice, Italy. cafe. tourist_trap. Historic cafe in St. Mark's Square..."
    }
  ]
}

---

## Deliverable

Produce the complete formatted database file ready for:
1. ChromaDB ingestion
2. JSON backup storage
3. Human review in Phase 5
```

---

## Phase 5: Verification & Sanity Check

```
# Phase 5: Tourist Trap RAG Database — Verification & Sanity Check

## Context
You have a formatted database of ~150 venues. Now perform comprehensive quality assurance before finalizing.

## Input
[INSERT PHASE 4 STRUCTURED DATA]

---

## Verification Checklist

### 5.1 Schema Validation
For EACH entry, verify:
- [ ] id follows pattern {category}-{name-slug}-{city-slug}
- [ ] id is unique (no duplicates)
- [ ] verdict is one of: tourist_trap, local_gem, mixed
- [ ] confidence is one of: high, medium, low
- [ ] tourist_trap_score is integer 0-100
- [ ] category is valid enum value
- [ ] At least 1 entry in red_flags array
- [ ] At least 1 entry in positive_signals array
- [ ] At least 2 entries in sample_reviews array
- [ ] embedding_text is populated and well-formed
- [ ] All required fields are present and non-empty

### 5.2 Score-Verdict Consistency
Check that scores align with verdicts:

| Verdict | Expected Score Range | Flag if Outside |
|---------|---------------------|-----------------|
| tourist_trap | 55-100 | Score < 55 is inconsistent |
| local_gem | 0-45 | Score > 45 is inconsistent |
| mixed | 35-65 | Score outside this range is inconsistent |

List all entries with score-verdict mismatches.

### 5.3 Evidence-Score Consistency
For entries with extreme scores, verify evidence supports it:
- Score 90-100: Should have 3+ severe red flags, overwhelming negative evidence
- Score 0-15: Should have 3+ strong positive signals, virtually no criticisms
- Score 45-55: Should have roughly balanced evidence

List any entries where evidence seems insufficient for the score.

### 5.4 Cross-Entry Consistency
Compare similar venues:
- Two restaurants in same city with similar descriptions should have similar scores
- Famous landmarks that are "worth it despite tourists" should be mixed, not local_gem
- Venues with identical red flags should have similar severity ratings

List any inconsistencies found.

### 5.5 Fabrication Check
Spot-check 20 random entries:
- Google the venue name + city to verify it exists
- Verify at least one quoted review can be found or is plausible
- Check that the summary matches publicly available information

List any entries that appear to have fabricated information.

### 5.6 Distribution Final Check
Verify final distribution meets targets:

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Total entries | 145-155 | ? | |
| tourist_trap % | 40-45% | ? | |
| local_gem % | 40-45% | ? | |
| mixed % | 10-15% | ? | |
| Restaurants % | 50-65% | ? | |
| High confidence % | >50% | ? | |
| Regions covered | 5 | ? | |
| Cities covered | 20+ | ? | |

---

## Output Format

{
  "phase": "verification",
  "verification_date": "YYYY-MM-DD",

  "schema_validation": {
    "total_entries_checked": 150,
    "entries_passing": 148,
    "entries_with_issues": [
      {
        "id": "entry-id",
        "issues": ["Missing required field: X", "Invalid category value"]
      }
    ]
  },

  "score_verdict_consistency": {
    "consistent_entries": 145,
    "inconsistent_entries": [
      {
        "id": "entry-id",
        "verdict": "tourist_trap",
        "score": 42,
        "issue": "Score too low for tourist_trap verdict",
        "recommendation": "Change verdict to 'mixed' OR increase score to 55+"
      }
    ]
  },

  "evidence_score_consistency": {
    "well_supported": 140,
    "questionable": [
      {
        "id": "entry-id",
        "score": 95,
        "issue": "Only 1 red flag documented, insufficient for score of 95",
        "recommendation": "Add more evidence OR reduce score to 70-80"
      }
    ]
  },

  "cross_entry_consistency": {
    "issues_found": [
      {
        "entries": ["entry-id-1", "entry-id-2"],
        "issue": "Both are upscale Paris restaurants with similar complaints but scores differ by 30 points",
        "recommendation": "Review and align scores"
      }
    ]
  },

  "fabrication_check": {
    "entries_spot_checked": 20,
    "verified_exist": 20,
    "evidence_plausible": 19,
    "concerns": [
      {
        "id": "entry-id",
        "concern": "Cannot find any source for quoted review",
        "recommendation": "Replace with verifiable quote or mark as paraphrased"
      }
    ]
  },

  "distribution_check": {
    "all_targets_met": true,
    "gaps": []
  },

  "overall_quality_score": "A | B | C | D | F",
  "ready_for_production": true,

  "required_fixes": [
    {
      "priority": "high | medium | low",
      "entry_id": "entry-id",
      "fix_description": "What needs to be fixed"
    }
  ],

  "summary": "Overall assessment of database quality and readiness"
}

---

## Fix Protocol

After verification, apply fixes in this order:
1. **High priority**: Schema violations, fabrication concerns
2. **Medium priority**: Score-verdict inconsistencies, missing evidence
3. **Low priority**: Minor formatting issues, distribution fine-tuning

---

## Final Deliverable

After all fixes are applied, produce:
1. **Final verified database** (JSON)
2. **Verification report** (this output)
3. **ChromaDB-ready format** with embeddings

The database is ready for production when:
- All high-priority fixes resolved
- Overall quality score is B or higher
- ready_for_production is true
```

---

## Quick Reference: Red Flags & Positive Signals

### Red Flag Types

| Type | Key Phrases |
|------|-------------|
| `price_quality_mismatch` | "overpriced", "ripoff", "not worth it", "tourist prices" |
| `authenticity_issues` | "not authentic", "Americanized", "touristy version", "fake" |
| `local_avoidance` | "locals don't eat here", "only tourists", "no locals in sight" |
| `service_problems` | "rushed out", "assembly line", "treated like cattle", "rude staff" |
| `quality_decline` | "used to be good", "gone downhill", "sold out" |
| `location_dependency` | "paying for the view", "location tax", "proximity to landmark" |
| `review_manipulation` | "fake reviews", "suspiciously positive", "bought reviews" |

### Positive Signal Types

| Type | Key Phrases |
|------|-------------|
| `local_endorsement` | "where locals go", "neighborhood favorite", "my regular spot" |
| `value_acknowledgment` | "worth every penny", "great value", "underpriced" |
| `authenticity_praise` | "authentic", "traditional", "real deal", "just like grandma's" |
| `repeat_visitors` | "come back every trip", "10th visit", "never disappoints" |
| `specific_quality` | Detailed praise about specific dishes, techniques, ingredients |

---

## RAG Database Expansion Prompt

```
# RAG Database Expansion: 50 → 150 Entries

## Task
Expand the existing RAG database from 50 to ~150 entries while preserving quality and improving balance/variety.

## Reference
- **Master Database**: @rag_v3.json (use as schema reference and quality benchmark)

## Gap Analysis Required

Before generating new entries, analyze the master database for:

### Geographic Gaps
Current coverage to evaluate: Europe (Paris, Rome, Barcelona, Venice, Amsterdam, etc.), Asia (Tokyo, Bangkok, etc.), Americas
- Identify underrepresented regions
- Target cities with high tourist traffic but low coverage

### Category Gaps
Current types: restaurant, cafe, bar, street_food, market, attraction
- Identify underrepresented categories
- Add more street_food, markets, and attractions if needed

### Verdict Balance
Target: 40-45% tourist_trap, 40-45% local_gem, 10-15% mixed
- Check current distribution
- Prioritize whichever verdict type is underrepresented

### Price Tier Balance
Target: 25-30% budget, 40-50% mid-range, 20-25% upscale, 5-10% luxury
- Check current distribution
- Fill gaps in underrepresented tiers

## Output Requirements

Generate **100 new entries** (for total ~150) following the EXACT schema from the master database:

- Match all field names and types exactly
- Use established red_flag and positive_signal types
- Maintain score-verdict alignment:
  - tourist_trap: score 55-100
  - local_gem: score 0-45
  - mixed: score 35-65
- Include 2-4 red_flags and 2-4 positive_signals per entry
- Include 2-3 sample_reviews per entry
- Generate proper embedding_text

## Quality Standards

- Each entry must have verifiable real-world evidence
- No fabricated quotes or reviews
- Diversify beyond obvious/famous examples
- Include some surprising classifications (famous places that are actually good, hidden traps)

## Batch Delivery

Deliver in batches of 20-25 entries for easier review.
```

---

## Batch Review Prompt (Analysis Only)

```
# RAG Batch Review — Analysis Only

## Task
Analyze the new batch for quality issues. Do NOT provide corrections—only flag problems for manual review.

## Reference Files
- **Master Database**: @rag_v3.json (schema and quality benchmark)
- **New Batch**: [batch file to review]

## Analysis Checklist

For each entry, check:

### Schema Compliance
- [ ] All required fields present
- [ ] Field types match master schema
- [ ] ID format: {category}-{name-slug}-{city-slug}

### Score-Verdict Alignment
- [ ] tourist_trap → score 55-100
- [ ] local_gem → score 0-45
- [ ] mixed → score 35-65

### Evidence Quality
- [ ] 2+ red_flags with descriptions and evidence
- [ ] 2+ positive_signals with descriptions and evidence
- [ ] 2+ sample_reviews from identifiable sources
- [ ] Summary reflects the evidence

### Consistency
- [ ] Similar venues have similar scores
- [ ] No duplicate entries (check against master)
- [ ] Geographic/category info is accurate

### Plausibility
- [ ] Venue appears to exist
- [ ] Reviews seem authentic (not fabricated)
- [ ] Classification matches known reputation

## Output Format

### Batch Summary
- Total entries reviewed: X
- Entries passing all checks: X
- Entries with issues: X

### Issues Found

For each problematic entry:

**Entry ID**: [id]
**Issue Type**: [schema | score_alignment | evidence | consistency | plausibility]
**Description**: [what's wrong]
**Severity**: [high | medium | low]

### Distribution Analysis
- Verdict breakdown of this batch
- Category breakdown
- Geographic coverage
- How this batch affects overall database balance

### Recommendation
- APPROVE / APPROVE WITH NOTES / NEEDS REVISION
```
