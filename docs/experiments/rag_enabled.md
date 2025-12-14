# Experiment: rag_enabled

## Metadata
- **Date:** 2025-12-14T22:24:20.599386
- **Runs per venue:** 5
- **Temperature:** default
- **RAG Enabled:** True

## Summary Metrics

### Accuracy
| Metric | Value |
|--------|-------|
| Classification Accuracy | 100.0% |
| Score Calibration | 50.0% |
| Mean Absolute Error | 15.95 |

### Consistency
| Metric | Value |
|--------|-------|
| Avg Score StdDev | 0.27 |
| Avg Score Range | 0.5 |
| Classification Consistency | 90.0% |
| Signal Stability | 100.0% |

### Quality
| Metric | Value |
|--------|-------|
| Avg Reasoning Length | 599 chars |
| Avg Evidence Count | 6.0 |

### Performance
| Metric | Value |
|--------|-------|
| Avg Latency | 3.4s |
| Total Time | 68.1s |

## Per-Venue Results

### Pizzeria Da Michele (Naples)
- **Expected:** authentic (score 5-35)
- **Ground Truth:** 25
- **Scores:** [20, 20, 20, 20, 20]
- **Mean:** 20.0, **StdDev:** 0.00, **MAE:** 5.0
- **Classification:** verified_authentic (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** Yes
- **Avg Latency:** 3.4s
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
- **Scores:** [70, 68, 68, 70, 68]
- **Mean:** 68.8, **StdDev:** 1.10, **MAE:** 18.8
- **Classification:** likely_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** No
- **Avg Latency:** 3.4s
- **Signal Stability:** 100%

### Katz's Delicatessen (New York)
- **Expected:** mixed (score 25-55)
- **Ground Truth:** 35
- **Scores:** [65, 65, 65, 65, 65]
- **Mean:** 65.0, **StdDev:** 0.00, **MAE:** 30.0
- **Classification:** likely_trap (60% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** No
- **Avg Latency:** 3.4s
- **Signal Stability:** 100%

## Comparison with Baseline
**Baseline:** baseline

| Metric | Baseline | Current | Change | Status |
|--------|----------|---------|--------|--------|
| Score Variance | 0.000 | 0.274 | +0.27 (+0.0%) | ➖ |
| Score Range | 0.000 | 0.500 | +0.50 (+0.0%) | ➖ |
| Mean Absolute Error | 21.250 | 15.950 | -5.30 (-24.9%) | ✅ |
| Classification Consistency | 1.000 | 0.900 | -0.10 (-10.0%) | ❌ |
| Classification Accuracy | 1.000 | 1.000 | +0.00 (+0.0%) | ➖ |
| Score Calibration | 0.500 | 0.500 | +0.00 (+0.0%) | ➖ |
| Avg Latency | 3.247 | 3.407 | +0.16 (+4.9%) | ❌ |
| Signal Stability | 1.000 | 1.000 | +0.00 (+0.0%) | ➖ |
| Reasoning Length | 591.250 | 599.100 | +7.85 (+1.3%) | ✅ |
| Evidence Count | 5.550 | 6.000 | +0.45 (+8.1%) | ✅ |

**Improved:** Mean Absolute Error, Evidence Count
**Degraded:** Classification Consistency, Avg Latency
**Unchanged:** Score Variance, Score Range, Classification Accuracy, Score Calibration, Signal Stability, Reasoning Length

## Decision Metrics

### Recommendation Score Components
- **Accuracy Score:** 100.0%
- **Consistency Score:** 88.8%
- **Performance Score:** 74.6%

---

**Raw Data:** [rag_enabled.json](rag_enabled.json)