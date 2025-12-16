# Experiment: rag_keyword

## Configuration
- **Date:** 2025-12-16T16:16:25.685537
- **Samples per category:** 10
- **Runs per venue:** 3
- **Temperature:** default
- **RAG Enabled:** True
- **RAG Mode:** keyword
- **Seed:** 42

## Summary

| Metric | Value |
|--------|-------|
| Venues Tested | 30/30 |
| Total Runs | 90/90 |
| Category Accuracy | 95.6% |
| Within ±15 pts | 93.3% |
| Within ±20 pts | 96.7% |
| Mean Absolute Error | 9.3 |
| Avg Score StdDev | 1.38 |
| Avg Latency | 2.8s |

## Per-Category Results

| Category | Count | Accuracy | Within ±15 | MAE | Avg Predicted |
|----------|-------|----------|------------|-----|---------------|
| local_gem | 10 | 100% | 100% | 8.7 | 24 |
| mixed | 10 | 90% | 90% | 10.7 | 50 |
| tourist_trap | 10 | 97% | 90% | 8.7 | 83 |

## Individual Venue Results

| Venue | Location | GT Verdict | GT Score | Predicted | Diff | Match |
|-------|----------|------------|----------|-----------|------|-------|
| L'As du Fallafel | Paris, France | local_gem | 18 | 25 | 7 | ✓ |
| Tim Ho Wan (Sham Shui Po) | Hong Kong | local_gem | 15 | 25 | 10 | ✓ |
| Ristorante Carlo Menta | Rome, Italy | mixed | 55 | 50 | 5 | ✓ |
| Pastéis de Belém | Lisbon, Portuga | local_gem | 25 | 25 | 0 | ✓ |
| Da Enzo al 29 | Rome, Italy | local_gem | 15 | 25 | 10 | ✓ |
| Antico Caffè Greco | Rome, Italy | mixed | 55 | 50 | 5 | ✓ |
| In-N-Out Burger | Los Angeles, US | local_gem | 10 | 25 | 15 | ✓ |
| Pink Mamma | Paris, France | tourist_trap | 65 | 72 | 7 | ✗ |
| Pujol | Mexico City, Me | mixed | 40 | 50 | 10 | ✓ |
| Angus Steakhouse | London, UK | tourist_trap | 95 | 95 | 0 | ✓ |
| Ichiran Shibuya | Tokyo, Japan | tourist_trap | 58 | 75 | 17 | ✓ |
| Gondola Rides | Venice, Italy | mixed | 55 | 52 | 3 | ✓ |
| Mona Lisa (The Louvre) | Paris, France | tourist_trap | 90 | 75 | 15 | ✓ |
| Bukchon Hanok Village | Seoul, South Ko | mixed | 60 | 50 | 10 | ✓ |
| Mercado de San Miguel | Madrid, Spain | mixed | 60 | 60 | 0 | ✓ |
| La Taqueria | San Francisco,  | local_gem | 20 | 18 | 5 | ✓ |
| Franklin Barbecue | Austin, USA | local_gem | 10 | 25 | 15 | ✓ |
| Roberta's (Bushwick) | New York, USA | local_gem | 15 | 25 | 10 | ✓ |
| Finns Beach Club | Bali, Indonesia | tourist_trap | 75 | 78 | 3 | ✓ |
| Wangfujing Snack Street | Beijing, China | tourist_trap | 95 | 90 | 5 | ✓ |
| Harry's Bar | Venice, Italy | mixed | 65 | 25 | 40 | ✗ |
| Ocean Drive Restaurants | Miami, USA | tourist_trap | 98 | 85 | 13 | ✓ |
| La Rambla Outdoor Restaur | Barcelona, Spai | tourist_trap | 98 | 85 | 13 | ✓ |
| Trdelník Stands (Old Town | Prague, Czech R | tourist_trap | 90 | 82 | 8 | ✓ |
| Swan Oyster Depot | San Francisco,  | local_gem | 15 | 25 | 10 | ✓ |
| Joe's Stone Crab | Miami, USA | local_gem | 30 | 25 | 5 | ✓ |
| Fisherman's Bastion | Budapest, Hunga | mixed | 45 | 58 | 13 | ✓ |
| Olive Garden Times Square | New York, USA | tourist_trap | 98 | 93 | 5 | ✓ |
| Escadaria Selarón | Rio de Janeiro, | mixed | 45 | 52 | 7 | ✓ |
| Duke's Waikiki | Honolulu, USA | mixed | 40 | 53 | 13 | ✓ |

---
**Raw Data:** [rag_keyword.json](rag_keyword.json)