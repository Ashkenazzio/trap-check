# Experiment: rag_vector

## Configuration
- **Date:** 2025-12-16T16:16:32.793440
- **Samples per category:** 10
- **Runs per venue:** 3
- **Temperature:** default
- **RAG Enabled:** True
- **RAG Mode:** vector
- **Seed:** 42

## Summary

| Metric | Value |
|--------|-------|
| Venues Tested | 30/30 |
| Total Runs | 90/90 |
| Category Accuracy | 94.4% |
| Within ±15 pts | 93.3% |
| Within ±20 pts | 96.7% |
| Mean Absolute Error | 9.9 |
| Avg Score StdDev | 2.06 |
| Avg Latency | 2.8s |

## Per-Category Results

| Category | Count | Accuracy | Within ±15 | MAE | Avg Predicted |
|----------|-------|----------|------------|-----|---------------|
| local_gem | 10 | 100% | 100% | 9.0 | 23 |
| mixed | 10 | 87% | 90% | 11.0 | 50 |
| tourist_trap | 10 | 97% | 90% | 9.5 | 84 |

## Individual Venue Results

| Venue | Location | GT Verdict | GT Score | Predicted | Diff | Match |
|-------|----------|------------|----------|-----------|------|-------|
| L'As du Fallafel | Paris, France | local_gem | 18 | 25 | 7 | ✓ |
| Tim Ho Wan (Sham Shui Po) | Hong Kong | local_gem | 15 | 25 | 10 | ✓ |
| Ristorante Carlo Menta | Rome, Italy | mixed | 55 | 50 | 5 | ✓ |
| Pastéis de Belém | Lisbon, Portuga | local_gem | 25 | 25 | 0 | ✓ |
| Da Enzo al 29 | Rome, Italy | local_gem | 15 | 25 | 10 | ✓ |
| Antico Caffè Greco | Rome, Italy | mixed | 55 | 48 | 7 | ✗ |
| In-N-Out Burger | Los Angeles, US | local_gem | 10 | 23 | 13 | ✓ |
| Pink Mamma | Paris, France | tourist_trap | 65 | 73 | 8 | ✗ |
| Pujol | Mexico City, Me | mixed | 40 | 50 | 10 | ✓ |
| Angus Steakhouse | London, UK | tourist_trap | 95 | 93 | 2 | ✓ |
| Ichiran Shibuya | Tokyo, Japan | tourist_trap | 58 | 75 | 17 | ✓ |
| Gondola Rides | Venice, Italy | mixed | 55 | 53 | 2 | ✓ |
| Mona Lisa (The Louvre) | Paris, France | tourist_trap | 90 | 75 | 15 | ✓ |
| Bukchon Hanok Village | Seoul, South Ko | mixed | 60 | 50 | 10 | ✓ |
| Mercado de San Miguel | Madrid, Spain | mixed | 60 | 62 | 2 | ✓ |
| La Taqueria | San Francisco,  | local_gem | 20 | 18 | 5 | ✓ |
| Franklin Barbecue | Austin, USA | local_gem | 10 | 25 | 15 | ✓ |
| Roberta's (Bushwick) | New York, USA | local_gem | 15 | 17 | 12 | ✓ |
| Finns Beach Club | Bali, Indonesia | tourist_trap | 75 | 85 | 10 | ✓ |
| Wangfujing Snack Street | Beijing, China | tourist_trap | 95 | 92 | 3 | ✓ |
| Harry's Bar | Venice, Italy | mixed | 65 | 25 | 40 | ✗ |
| Ocean Drive Restaurants | Miami, USA | tourist_trap | 98 | 85 | 13 | ✓ |
| La Rambla Outdoor Restaur | Barcelona, Spai | tourist_trap | 98 | 85 | 13 | ✓ |
| Trdelník Stands (Old Town | Prague, Czech R | tourist_trap | 90 | 82 | 8 | ✓ |
| Swan Oyster Depot | San Francisco,  | local_gem | 15 | 25 | 10 | ✓ |
| Joe's Stone Crab | Miami, USA | local_gem | 30 | 22 | 8 | ✓ |
| Fisherman's Bastion | Budapest, Hunga | mixed | 45 | 57 | 12 | ✓ |
| Olive Garden Times Square | New York, USA | tourist_trap | 98 | 92 | 6 | ✓ |
| Escadaria Selarón | Rio de Janeiro, | mixed | 45 | 55 | 10 | ✓ |
| Duke's Waikiki | Honolulu, USA | mixed | 40 | 53 | 13 | ✓ |

---
**Raw Data:** [rag_vector.json](rag_vector.json)