# Experiment: baseline

## Metadata
- **Date:** 2025-12-14T21:57:38.278690
- **Runs per venue:** 5
- **Temperature:** default
- **RAG Enabled:** False

## Summary Metrics

### Accuracy
| Metric | Value |
|--------|-------|
| Classification Accuracy | 100.0% |
| Score Calibration | 50.0% |
| Mean Absolute Error | 21.25 |

### Consistency
| Metric | Value |
|--------|-------|
| Avg Score StdDev | 0.00 |
| Avg Score Range | 0.0 |
| Classification Consistency | 100.0% |
| Signal Stability | 100.0% |

### Quality
| Metric | Value |
|--------|-------|
| Avg Reasoning Length | 591 chars |
| Avg Evidence Count | 5.5 |

### Performance
| Metric | Value |
|--------|-------|
| Avg Latency | 3.2s |
| Total Time | 64.9s |

## Per-Venue Results

### Pizzeria Da Michele (Naples)
- **Expected:** authentic (score 5-35)
- **Ground Truth:** 25
- **Scores:** [25, 25, 25, 25, 25]
- **Mean:** 25.0, **StdDev:** 0.00, **MAE:** 0.0
- **Classification:** likely_authentic (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** Yes
- **Avg Latency:** 3.3s
- **Signal Stability:** 100%

### Olive Garden Times Square (New York)
- **Expected:** trap (score 65-95)
- **Ground Truth:** 85
- **Scores:** [95, 95, 95, 95, 95]
- **Mean:** 95.0, **StdDev:** 0.00, **MAE:** 10.0
- **Classification:** definite_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** Yes
- **Avg Latency:** 3.1s
- **Signal Stability:** 100%

### Carlo Menta (Rome)
- **Expected:** mixed (score 35-65)
- **Ground Truth:** 50
- **Scores:** [85, 85, 85, 85, 85]
- **Mean:** 85.0, **StdDev:** 0.00, **MAE:** 35.0
- **Classification:** likely_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** No
- **Avg Latency:** 3.3s
- **Signal Stability:** 100%

### Katz's Delicatessen (New York)
- **Expected:** mixed (score 25-55)
- **Ground Truth:** 35
- **Scores:** [75, 75, 75, 75, 75]
- **Mean:** 75.0, **StdDev:** 0.00, **MAE:** 40.0
- **Classification:** likely_trap (100% consistent)
- **Classification Accuracy:** 100%
- **In Expected Range:** No
- **Avg Latency:** 3.3s
- **Signal Stability:** 100%

## Decision Metrics

### Recommendation Score Components
- **Accuracy Score:** 100.0%
- **Consistency Score:** 100.0%
- **Performance Score:** 75.5%

---

**Raw Data:** [baseline.json](baseline.json)