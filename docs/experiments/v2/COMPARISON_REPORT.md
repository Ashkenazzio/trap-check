# TrapCheck Evaluation v2 - Comparison Report

**Date:** 2025-12-16
**Test Set:** 30 venues (10 per category: trap/gem/mixed), 3 runs each = 90 runs per experiment
**Seed:** 42 (reproducible sampling)

## Executive Summary

| Experiment | Category Accuracy | Within ±15 | MAE | StdDev | Best At |
|------------|-------------------|------------|-----|--------|---------|
| baseline | 90.0% | 77.8% | 13.6 | 3.27 | - |
| temp_0.0 | 90.0% | 84.4% | 12.7 | **1.64** | Consistency |
| temp_0.5 | 90.0% | 81.1% | 13.0 | 2.19 | - |
| **rag_keyword** | **95.6%** | **93.3%** | **9.3** | 1.38 | **Overall Winner** |
| rag_vector | 94.4% | 93.3% | 9.9 | 2.06 | - |

## Key Findings

### 1. RAG Significantly Improves Accuracy

RAG calibration examples provide **5.6% improvement** in category accuracy:
- Baseline: 90.0% → RAG Keyword: 95.6%
- MAE reduced by **32%** (13.6 → 9.3)
- Within ±15 pts improved by **15.5%** (77.8% → 93.3%)

### 2. Temperature Has Minimal Effect on Accuracy

All temperature settings achieved identical 90% category accuracy:
- temp_0.0: More consistent (StdDev 1.64 vs 3.27)
- temp_0.5: Slightly more consistent (StdDev 2.19)
- Default temp: Most variance but same accuracy

### 3. Keyword RAG Outperforms Vector RAG

| Metric | Keyword | Vector |
|--------|---------|--------|
| Category Accuracy | **95.6%** | 94.4% |
| MAE | **9.3** | 9.9 |
| Consistency (StdDev) | **1.38** | 2.06 |
| Latency | **2.8s** | 2.8s |

Keyword RAG is recommended for production.

### 4. "Mixed" Category Remains Challenging

| Experiment | Trap Acc | Gem Acc | Mixed Acc |
|------------|----------|---------|-----------|
| baseline | 100% | 100% | 70% |
| temp_0.0 | 100% | 100% | 70% |
| rag_keyword | 97% | 100% | **90%** |
| rag_vector | 97% | 100% | 87% |

RAG improves mixed accuracy from 70% to 90%.

## Per-Category Performance

### Tourist Traps (10 venues)
| Experiment | Accuracy | MAE | Avg Predicted |
|------------|----------|-----|---------------|
| baseline | 100% | 9.9 | 86 |
| rag_keyword | 97% | **8.7** | 83 |
| rag_vector | 97% | 9.5 | 84 |

### Local Gems (10 venues)
| Experiment | Accuracy | MAE | Avg Predicted |
|------------|----------|-----|---------------|
| baseline | 100% | 14.8 | 4 |
| rag_keyword | 100% | **8.7** | 23 |
| rag_vector | 100% | 9.0 | 22 |

RAG fixes the "over-confident authentic" problem (predicting 0 instead of 15-25).

### Mixed (10 venues)
| Experiment | Accuracy | MAE | Avg Predicted |
|------------|----------|-----|---------------|
| baseline | 70% | 16.2 | 48 |
| rag_keyword | **90%** | **10.7** | 50 |
| rag_vector | 87% | 11.0 | 51 |

## Problematic Venues

### Consistently Misclassified Across All Experiments

**Harry's Bar (Venice)** - GT: mixed (65)
- All experiments predict 0-25 (not_trap)
- Issue: Synthetic data may not capture the "expensive but historical" mixed signals

### Improved by RAG

**Bukchon Hanok Village** - GT: mixed (60)
- Baseline: 25 (wrong) → RAG Keyword: 50 (correct)

**Mercado de San Miguel** - GT: mixed (60)
- Baseline: 75 (wrong) → RAG Keyword: 60 (exact match!)

## Recommendations

1. **Use RAG Keyword mode** for production - best accuracy with minimal overhead
2. **Temperature 0.0** if consistency is critical (lower variance)
3. **Investigate Harry's Bar** - persistent misclassification suggests ground truth or synthetic data issue
4. **Mixed venues need more calibration examples** in RAG database

## Raw Data

- [baseline.json](baseline.json) / [baseline.md](baseline.md)
- [temp_0.0.json](temp_0.0.json) / [temp_0.0.md](temp_0.0.md)
- [temp_0.5.json](temp_0.5.json) / [temp_0.5.md](temp_0.5.md)
- [rag_keyword.json](rag_keyword.json) / [rag_keyword.md](rag_keyword.md)
- [rag_vector.json](rag_vector.json) / [rag_vector.md](rag_vector.md)
