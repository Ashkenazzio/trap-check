# Experiment: [EXPERIMENT NAME]

## Metadata
- **Date:** [YYYY-MM-DD]
- **Experiment ID:** [baseline|temp_0.0|temp_0.5|temp_1.0|rag_enabled|...]
- **Configuration:** [Brief description of system state]

## Objective
[What are we testing/measuring?]

## Hypothesis
[What do we expect to happen?]

## Method
- Runs per venue: [N]
- Delay between runs: [X seconds]
- Venues tested: [List]
- Special conditions: [Any modifications to code/prompts]

## Configuration Details
```
Temperature: [value or default]
RAG enabled: [yes/no]
RAG examples per verdict: [N]
```

## Results

### Per-Venue Results

#### Pizzeria Da Michele (Naples)
- **Expected:** Authentic (score 5-35), Ground Truth: 25
- **Scores:** [list]
- **Mean:** [X], **StdDev:** [Y], **MAE:** [Z]
- **Range:** [min-max] (spread: [Z])
- **Classifications:** [list]
- **Classification Accuracy:** [X%]
- **Consistency:** [X/N same classification]
- **In expected range:** [yes/no]

#### Olive Garden Times Square (NYC)
- **Expected:** Trap (score 65-95), Ground Truth: 85
- **Scores:** [list]
- **Mean:** [X], **StdDev:** [Y], **MAE:** [Z]
- **Range:** [min-max] (spread: [Z])
- **Classifications:** [list]
- **Classification Accuracy:** [X%]
- **Consistency:** [X/N same classification]
- **In expected range:** [yes/no]

#### Carlo Menta (Rome)
- **Expected:** Mixed (score 35-65), Ground Truth: 50
- **Scores:** [list]
- **Mean:** [X], **StdDev:** [Y], **MAE:** [Z]
- **Range:** [min-max] (spread: [Z])
- **Classifications:** [list]
- **Classification Accuracy:** [X%]
- **Consistency:** [X/N same classification]
- **In expected range:** [yes/no]

#### Katz's Delicatessen (NYC)
- **Expected:** Mixed (score 25-55), Ground Truth: 35
- **Scores:** [list]
- **Mean:** [X], **StdDev:** [Y], **MAE:** [Z]
- **Range:** [min-max] (spread: [Z])
- **Classifications:** [list]
- **Classification Accuracy:** [X%]
- **Consistency:** [X/N same classification]
- **In expected range:** [yes/no]

### Aggregate Metrics

| Metric | Value |
|--------|-------|
| Classification Accuracy | [X%] |
| Score Calibration | [X%] |
| Mean Absolute Error | [X] |
| Average StdDev | [X] |
| Average Score Range | [X] |
| Avg Classification Consistency | [X%] |
| Signal Stability | [X%] |
| Avg Latency | [X]s |

## Analysis

### What Worked
- [Observations about what went well]

### What Didn't Work
- [Observations about problems or unexpected results]

### Key Insights
- [Important learnings from this experiment]

## Comparison to Baseline

| Metric | Baseline | This Experiment | Change |
|--------|----------|-----------------|--------|
| Avg StdDev | [X] | [Y] | [±Z%] |
| Avg MAE | [X] | [Y] | [±Z%] |
| Classification Accuracy | [X%] | [Y%] | [±Z%] |
| Classification Consistency | [X%] | [Y%] | [±Z%] |
| Avg Latency | [X]s | [Y]s | [±Z%] |

## Conclusions
[Summary of findings and implications for next steps]

## Next Actions
- [ ] [Action item 1]
- [ ] [Action item 2]

---

## Raw Data

<details>
<summary>Full JSON Results</summary>

```json
[Paste evaluation.py output here]
```

</details>
