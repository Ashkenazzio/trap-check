# Experiment: baseline

## Configuration
- **Date:** 2025-12-16T16:04:27.597894
- **Samples per category:** 10
- **Runs per venue:** 3
- **Temperature:** default
- **RAG Enabled:** False
- **RAG Mode:** N/A
- **Seed:** 42

## Summary

| Metric | Value |
|--------|-------|
| Venues Tested | 30/30 |
| Total Runs | 90/90 |
| Category Accuracy | 90.0% |
| Within ±15 pts | 77.8% |
| Within ±20 pts | 85.6% |
| Mean Absolute Error | 13.6 |
| Avg Score StdDev | 3.27 |
| Avg Latency | 3.0s |

## Per-Category Results

| Category | Count | Accuracy | Within ±15 | MAE | Avg Predicted |
|----------|-------|----------|------------|-----|---------------|
| local_gem | 10 | 100% | 73% | 14.8 | 4 |
| mixed | 10 | 70% | 73% | 16.2 | 48 |
| tourist_trap | 10 | 100% | 87% | 9.9 | 86 |

## Individual Venue Results

| Venue | Location | GT Verdict | GT Score | Predicted | Diff | Match |
|-------|----------|------------|----------|-----------|------|-------|
| L'As du Fallafel | Paris, France | local_gem | 18 | 0 | 18 | ✓ |
| Tim Ho Wan (Sham Shui Po) | Hong Kong | local_gem | 15 | 0 | 15 | ✓ |
| Ristorante Carlo Menta | Rome, Italy | mixed | 55 | 53 | 5 | ✓ |
| Pastéis de Belém | Lisbon, Portuga | local_gem | 25 | 0 | 25 | ✓ |
| Da Enzo al 29 | Rome, Italy | local_gem | 15 | 0 | 15 | ✓ |
| Antico Caffè Greco | Rome, Italy | mixed | 55 | 57 | 5 | ✓ |
| In-N-Out Burger | Los Angeles, US | local_gem | 10 | 0 | 10 | ✓ |
| Pink Mamma | Paris, France | tourist_trap | 65 | 75 | 10 | ✓ |
| Pujol | Mexico City, Me | mixed | 40 | 50 | 10 | ✓ |
| Angus Steakhouse | London, UK | tourist_trap | 95 | 93 | 2 | ✓ |
| Ichiran Shibuya | Tokyo, Japan | tourist_trap | 58 | 85 | 27 | ✓ |
| Gondola Rides | Venice, Italy | mixed | 55 | 53 | 5 | ✓ |
| Mona Lisa (The Louvre) | Paris, France | tourist_trap | 90 | 73 | 17 | ✓ |
| Bukchon Hanok Village | Seoul, South Ko | mixed | 60 | 25 | 35 | ✗ |
| Mercado de San Miguel | Madrid, Spain | mixed | 60 | 75 | 15 | ✗ |
| La Taqueria | San Francisco,  | local_gem | 20 | 17 | 10 | ✓ |
| Franklin Barbecue | Austin, USA | local_gem | 10 | 8 | 12 | ✓ |
| Roberta's (Bushwick) | New York, USA | local_gem | 15 | 0 | 15 | ✓ |
| Finns Beach Club | Bali, Indonesia | tourist_trap | 75 | 85 | 10 | ✓ |
| Wangfujing Snack Street | Beijing, China | tourist_trap | 95 | 93 | 2 | ✓ |
| Harry's Bar | Venice, Italy | mixed | 65 | 8 | 57 | ✗ |
| Ocean Drive Restaurants | Miami, USA | tourist_trap | 98 | 90 | 8 | ✓ |
| La Rambla Outdoor Restaur | Barcelona, Spai | tourist_trap | 98 | 85 | 13 | ✓ |
| Trdelník Stands (Old Town | Prague, Czech R | tourist_trap | 90 | 87 | 3 | ✓ |
| Swan Oyster Depot | San Francisco,  | local_gem | 15 | 0 | 15 | ✓ |
| Joe's Stone Crab | Miami, USA | local_gem | 30 | 17 | 13 | ✓ |
| Fisherman's Bastion | Budapest, Hunga | mixed | 45 | 53 | 8 | ✓ |
| Olive Garden Times Square | New York, USA | tourist_trap | 98 | 90 | 8 | ✓ |
| Escadaria Selarón | Rio de Janeiro, | mixed | 45 | 50 | 5 | ✓ |
| Duke's Waikiki | Honolulu, USA | mixed | 40 | 57 | 17 | ✓ |

---
**Raw Data:** [baseline.json](baseline.json)