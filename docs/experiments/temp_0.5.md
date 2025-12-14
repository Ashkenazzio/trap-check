# Experiment: temp_0.5

## Metadata
- **Date:** 2025-12-14T22:04:30.870893
- **Runs per venue:** 5
- **Temperature:** 0.5
- **RAG Enabled:** False

## Summary Metrics

### Accuracy
| Metric | Value |
|--------|-------|
| Classification Accuracy | 100.0% |
| Score Calibration | 50.0% |
| Mean Absolute Error | 21.55 |

### Consistency
| Metric | Value |
|--------|-------|
| Avg Score StdDev | 0.41 |
| Avg Score Range | 0.8 |
| Classification Consistency | 100.0% |
| Signal Stability | 100.0% |

### Quality
| Metric | Value |
|--------|-------|
| Avg Reasoning Length | 629 chars |
| Avg Evidence Count | 5.9 |

### Performance
| Metric | Value |
|--------|-------|
| Avg Latency | 3.4s |
| Total Time | 67.6s |

## Per-Venue Results

### Pizzeria Da Michele (Naples)
- **Expected:** authentic (score 5-35)
- **Ground Truth:** 25
- **Scores:** [25, 25, 25, 25, 25]
- **Mean:** 25.0, **StdDev:** 0.00, **MAE:** 0.0
- **Classification:** likely_authentic (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** Yes
- **Avg Latency:** 3.5s
- **Signal Stability:** 100%

### Olive Garden Times Square (New York)
- **Expected:** trap (score 65-95)
- **Ground Truth:** 85
- **Scores:** [95, 95, 95, 95, 95]
- **Mean:** 95.0, **StdDev:** 0.00, **MAE:** 10.0
- **Classification:** definite_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** Yes
- **Avg Latency:** 3.2s
- **Signal Stability:** 100%

### Carlo Menta (Rome)
- **Expected:** mixed (score 35-65)
- **Ground Truth:** 50
- **Scores:** [85, 85, 85, 85, 85]
- **Mean:** 85.0, **StdDev:** 0.00, **MAE:** 35.0
- **Classification:** likely_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** No
- **Avg Latency:** 3.5s
- **Signal Stability:** 100%

### Katz's Delicatessen (New York)
- **Expected:** mixed (score 25-55)
- **Ground Truth:** 35
- **Scores:** [78, 75, 78, 75, 75]
- **Mean:** 76.2, **StdDev:** 1.64, **MAE:** 41.2
- **Classification:** likely_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** No
- **Avg Latency:** 3.4s
- **Signal Stability:** 100%

## Comparison with Baseline
**Baseline:** baseline

| Metric | Baseline | Current | Change | Status |
|--------|----------|---------|--------|--------|
| Score Variance | 0.000 | 0.411 | +0.41 (+0.0%) | ➖ |
| Score Range | 0.000 | 0.750 | +0.75 (+0.0%) | ➖ |
| Mean Absolute Error | 21.250 | 21.550 | +0.30 (+1.4%) | ➖ |
| Classification Consistency | 1.000 | 1.000 | +0.00 (+0.0%) | ➖ |
| Classification Accuracy | 1.000 | 1.000 | +0.00 (+0.0%) | ➖ |
| Score Calibration | 0.500 | 0.500 | +0.00 (+0.0%) | ➖ |
| Avg Latency | 3.247 | 3.380 | +0.13 (+4.1%) | ❌ |
| Signal Stability | 1.000 | 1.000 | +0.00 (+0.0%) | ➖ |
| Reasoning Length | 591.250 | 628.550 | +37.30 (+6.3%) | ✅ |
| Evidence Count | 5.550 | 5.900 | +0.35 (+6.3%) | ✅ |

**Improved:** Reasoning Length, Evidence Count
**Degraded:** Avg Latency
**Unchanged:** Score Variance, Score Range, Mean Absolute Error, Classification Consistency, Classification Accuracy, Score Calibration, Signal Stability

## Decision Metrics

### Recommendation Score Components
- **Accuracy Score:** 100.0%
- **Consistency Score:** 97.9%
- **Performance Score:** 74.7%

---

**Raw Data:** [temp_0.5.json](temp_0.5.json)