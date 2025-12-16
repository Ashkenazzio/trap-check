# Experiment: rag_keyword

## Metadata
- **Date:** 2025-12-14T23:04:18.491806
- **Runs per venue:** 5
- **Temperature:** default
- **RAG Enabled:** True

## Summary Metrics

### Accuracy
| Metric | Value |
|--------|-------|
| Classification Accuracy | 100.0% |
| Score Calibration | 50.0% |
| Mean Absolute Error | 17.45 |

### Consistency
| Metric | Value |
|--------|-------|
| Avg Score StdDev | 1.19 |
| Avg Score Range | 2.5 |
| Classification Consistency | 100.0% |
| Signal Stability | 100.0% |

### Quality
| Metric | Value |
|--------|-------|
| Avg Reasoning Length | 604 chars |
| Avg Evidence Count | 5.8 |

### Performance
| Metric | Value |
|--------|-------|
| Avg Latency | 3.3s |
| Total Time | 66.9s |

## Per-Venue Results

### Pizzeria Da Michele (Naples)
- **Expected:** authentic (score 5-35)
- **Ground Truth:** 25
- **Scores:** [20, 20, 20, 20, 20]
- **Mean:** 20.0, **StdDev:** 0.00, **MAE:** 5.0
- **Classification:** verified_authentic (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** Yes
- **Avg Latency:** 3.2s
- **Signal Stability:** 100%

### Olive Garden Times Square (New York)
- **Expected:** trap (score 65-95)
- **Ground Truth:** 85
- **Scores:** [95, 95, 95, 95, 95]
- **Mean:** 95.0, **StdDev:** 0.00, **MAE:** 10.0
- **Classification:** definite_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** Yes
- **Avg Latency:** 3.4s
- **Signal Stability:** 100%

### Carlo Menta (Rome)
- **Expected:** mixed (score 35-65)
- **Ground Truth:** 50
- **Scores:** [75, 75, 68, 75, 75]
- **Mean:** 73.6, **StdDev:** 3.13, **MAE:** 23.6
- **Classification:** likely_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** No
- **Avg Latency:** 3.3s
- **Signal Stability:** 100%

### Katz's Delicatessen (New York)
- **Expected:** mixed (score 25-55)
- **Ground Truth:** 35
- **Scores:** [68, 65, 68, 65, 65]
- **Mean:** 66.2, **StdDev:** 1.64, **MAE:** 31.2
- **Classification:** likely_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** No
- **Avg Latency:** 3.4s
- **Signal Stability:** 100%

## Comparison with Baseline
**Baseline:** baseline

| Metric | Baseline | Current | Change | Status |
|--------|----------|---------|--------|--------|
| Score Variance | 0.000 | 1.193 | +1.19 (+0.0%) | ➖ |
| Score Range | 0.000 | 2.500 | +2.50 (+0.0%) | ➖ |
| Mean Absolute Error | 21.250 | 17.450 | -3.80 (-17.9%) | ✅ |
| Classification Consistency | 1.000 | 1.000 | +0.00 (+0.0%) | ➖ |
| Classification Accuracy | 1.000 | 1.000 | +0.00 (+0.0%) | ➖ |
| Score Calibration | 0.500 | 0.500 | +0.00 (+0.0%) | ➖ |
| Avg Latency | 3.247 | 3.347 | +0.10 (+3.1%) | ❌ |
| Signal Stability | 1.000 | 1.000 | +0.00 (+0.0%) | ➖ |
| Reasoning Length | 591.250 | 604.150 | +12.90 (+2.2%) | ✅ |
| Evidence Count | 5.550 | 5.850 | +0.30 (+5.4%) | ✅ |

**Improved:** Mean Absolute Error, Reasoning Length, Evidence Count
**Degraded:** Avg Latency
**Unchanged:** Score Variance, Score Range, Classification Consistency, Classification Accuracy, Score Calibration, Signal Stability

## Decision Metrics

### Recommendation Score Components
- **Accuracy Score:** 100.0%
- **Consistency Score:** 94.0%
- **Performance Score:** 74.9%

---

**Raw Data:** [rag_keyword.json](rag_keyword.json)