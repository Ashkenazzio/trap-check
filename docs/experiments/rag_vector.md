# Experiment: rag_vector

## Metadata
- **Date:** 2025-12-14T22:52:22.695615
- **Runs per venue:** 5
- **Temperature:** default
- **RAG Enabled:** True

## Summary Metrics

### Accuracy
| Metric | Value |
|--------|-------|
| Classification Accuracy | 100.0% |
| Score Calibration | 50.0% |
| Mean Absolute Error | 18.05 |

### Consistency
| Metric | Value |
|--------|-------|
| Avg Score StdDev | 1.10 |
| Avg Score Range | 2.0 |
| Classification Consistency | 100.0% |
| Signal Stability | 100.0% |

### Quality
| Metric | Value |
|--------|-------|
| Avg Reasoning Length | 598 chars |
| Avg Evidence Count | 6.0 |

### Performance
| Metric | Value |
|--------|-------|
| Avg Latency | 4.1s |
| Total Time | 82.0s |

## Per-Venue Results

### Pizzeria Da Michele (Naples)
- **Expected:** authentic (score 5-35)
- **Ground Truth:** 25
- **Scores:** [20, 25, 20, 20, 25]
- **Mean:** 22.0, **StdDev:** 2.74, **MAE:** 3.0
- **Classification:** verified_authentic (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** Yes
- **Avg Latency:** 6.0s
- **Signal Stability:** 100%

### Olive Garden Times Square (New York)
- **Expected:** trap (score 65-95)
- **Ground Truth:** 85
- **Scores:** [95, 95, 95, 95, 95]
- **Mean:** 95.0, **StdDev:** 0.00, **MAE:** 10.0
- **Classification:** definite_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** Yes
- **Avg Latency:** 3.5s
- **Signal Stability:** 100%

### Carlo Menta (Rome)
- **Expected:** mixed (score 35-65)
- **Ground Truth:** 50
- **Scores:** [78, 75, 75, 78, 75]
- **Mean:** 76.2, **StdDev:** 1.64, **MAE:** 26.2
- **Classification:** likely_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** No
- **Avg Latency:** 3.4s
- **Signal Stability:** 100%

### Katz's Delicatessen (New York)
- **Expected:** mixed (score 25-55)
- **Ground Truth:** 35
- **Scores:** [68, 68, 68, 68, 68]
- **Mean:** 68.0, **StdDev:** 0.00, **MAE:** 33.0
- **Classification:** likely_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** No
- **Avg Latency:** 3.5s
- **Signal Stability:** 100%

## Comparison with Baseline
**Baseline:** baseline

| Metric | Baseline | Current | Change | Status |
|--------|----------|---------|--------|--------|
| Score Variance | 0.000 | 1.095 | +1.09 (+0.0%) | ➖ |
| Score Range | 0.000 | 2.000 | +2.00 (+0.0%) | ➖ |
| Mean Absolute Error | 21.250 | 18.050 | -3.20 (-15.1%) | ✅ |
| Classification Consistency | 1.000 | 1.000 | +0.00 (+0.0%) | ➖ |
| Classification Accuracy | 1.000 | 1.000 | +0.00 (+0.0%) | ➖ |
| Score Calibration | 0.500 | 0.500 | +0.00 (+0.0%) | ➖ |
| Avg Latency | 3.247 | 4.101 | +0.85 (+26.3%) | ❌ |
| Signal Stability | 1.000 | 1.000 | +0.00 (+0.0%) | ➖ |
| Reasoning Length | 591.250 | 598.200 | +6.95 (+1.2%) | ✅ |
| Evidence Count | 5.550 | 6.000 | +0.45 (+8.1%) | ✅ |

**Improved:** Mean Absolute Error, Evidence Count
**Degraded:** Avg Latency
**Unchanged:** Score Variance, Score Range, Classification Consistency, Classification Accuracy, Score Calibration, Signal Stability, Reasoning Length

## Decision Metrics

### Recommendation Score Components
- **Accuracy Score:** 100.0%
- **Consistency Score:** 94.5%
- **Performance Score:** 70.9%

---

**Raw Data:** [rag_vector.json](rag_vector.json)