# Experiment: test_run

## Configuration
- **Date:** 2025-12-16T15:57:52.269964
- **Samples per category:** 1
- **Runs per venue:** 1
- **Temperature:** default
- **RAG Enabled:** False
- **RAG Mode:** N/A
- **Seed:** 42

## Summary

| Metric | Value |
|--------|-------|
| Venues Tested | 3/3 |
| Total Runs | 3/3 |
| Category Accuracy | 66.7% |
| Within ±15 pts | 66.7% |
| Within ±20 pts | 100.0% |
| Mean Absolute Error | 15.7 |
| Avg Score StdDev | 0.00 |
| Avg Latency | 3.1s |

## Per-Category Results

| Category | Count | Accuracy | Within ±15 | MAE | Avg Predicted |
|----------|-------|----------|------------|-----|---------------|
| local_gem | 1 | 100% | 100% | 15.0 | 0 |
| mixed | 1 | 0% | 100% | 15.0 | 75 |
| tourist_trap | 1 | 100% | 0% | 17.0 | 75 |

## Individual Venue Results

| Venue | Location | GT Verdict | GT Score | Predicted | Diff | Match |
|-------|----------|------------|----------|-----------|------|-------|
| Da Enzo al 29 | Rome, Italy | local_gem | 15 | 0 | 15 | ✓ |
| Mercado de San Miguel | Madrid, Spain | mixed | 60 | 75 | 15 | ✗ |
| Ichiran Shibuya | Tokyo, Japan | tourist_trap | 58 | 75 | 17 | ✓ |

---
**Raw Data:** [test_run.json](test_run.json)