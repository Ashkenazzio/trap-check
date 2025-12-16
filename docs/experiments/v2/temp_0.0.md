# Experiment: temp_0.0

## Configuration
- **Date:** 2025-12-16T16:16:08.642821
- **Samples per category:** 10
- **Runs per venue:** 3
- **Temperature:** 0.0
- **RAG Enabled:** False
- **RAG Mode:** N/A
- **Seed:** 42

## Summary

| Metric | Value |
|--------|-------|
| Venues Tested | 30/30 |
| Total Runs | 90/90 |
| Category Accuracy | 90.0% |
| Within ±15 pts | 84.4% |
| Within ±20 pts | 87.8% |
| Mean Absolute Error | 12.7 |
| Avg Score StdDev | 1.64 |
| Avg Latency | 2.7s |

## Per-Category Results

| Category | Count | Accuracy | Within ±15 | MAE | Avg Predicted |
|----------|-------|----------|------------|-----|---------------|
| local_gem | 10 | 100% | 83% | 12.6 | 8 |
| mixed | 10 | 70% | 80% | 14.0 | 49 |
| tourist_trap | 10 | 100% | 90% | 11.6 | 84 |

## Individual Venue Results

| Venue | Location | GT Verdict | GT Score | Predicted | Diff | Match |
|-------|----------|------------|----------|-----------|------|-------|
| L'As du Fallafel | Paris, France | local_gem | 18 | 0 | 18 | ✓ |
| Tim Ho Wan (Sham Shui Po) | Hong Kong | local_gem | 15 | 8 | 13 | ✓ |
| Ristorante Carlo Menta | Rome, Italy | mixed | 55 | 57 | 5 | ✓ |
| Pastéis de Belém | Lisbon, Portuga | local_gem | 25 | 8 | 17 | ✓ |
| Da Enzo al 29 | Rome, Italy | local_gem | 15 | 0 | 15 | ✓ |
| Antico Caffè Greco | Rome, Italy | mixed | 55 | 50 | 5 | ✓ |
| In-N-Out Burger | Los Angeles, US | local_gem | 10 | 0 | 10 | ✓ |
| Pink Mamma | Paris, France | tourist_trap | 65 | 75 | 10 | ✓ |
| Pujol | Mexico City, Me | mixed | 40 | 50 | 10 | ✓ |
| Angus Steakhouse | London, UK | tourist_trap | 95 | 95 | 0 | ✓ |
| Ichiran Shibuya | Tokyo, Japan | tourist_trap | 58 | 85 | 27 | ✓ |
| Gondola Rides | Venice, Italy | mixed | 55 | 50 | 5 | ✓ |
| Mona Lisa (The Louvre) | Paris, France | tourist_trap | 90 | 75 | 15 | ✓ |
| Bukchon Hanok Village | Seoul, South Ko | mixed | 60 | 25 | 35 | ✗ |
| Mercado de San Miguel | Madrid, Spain | mixed | 60 | 75 | 15 | ✗ |
| La Taqueria | San Francisco,  | local_gem | 20 | 25 | 5 | ✓ |
| Franklin Barbecue | Austin, USA | local_gem | 10 | 17 | 13 | ✓ |
| Roberta's (Bushwick) | New York, USA | local_gem | 15 | 0 | 15 | ✓ |
| Finns Beach Club | Bali, Indonesia | tourist_trap | 75 | 85 | 10 | ✓ |
| Wangfujing Snack Street | Beijing, China | tourist_trap | 95 | 85 | 10 | ✓ |
| Harry's Bar | Venice, Italy | mixed | 65 | 25 | 40 | ✗ |
| Ocean Drive Restaurants | Miami, USA | tourist_trap | 98 | 85 | 13 | ✓ |
| La Rambla Outdoor Restaur | Barcelona, Spai | tourist_trap | 98 | 85 | 13 | ✓ |
| Trdelník Stands (Old Town | Prague, Czech R | tourist_trap | 90 | 85 | 5 | ✓ |
| Swan Oyster Depot | San Francisco,  | local_gem | 15 | 0 | 15 | ✓ |
| Joe's Stone Crab | Miami, USA | local_gem | 30 | 25 | 5 | ✓ |
| Fisherman's Bastion | Budapest, Hunga | mixed | 45 | 50 | 5 | ✓ |
| Olive Garden Times Square | New York, USA | tourist_trap | 98 | 85 | 13 | ✓ |
| Escadaria Selarón | Rio de Janeiro, | mixed | 45 | 55 | 10 | ✓ |
| Duke's Waikiki | Honolulu, USA | mixed | 40 | 50 | 10 | ✓ |

---
**Raw Data:** [temp_0.0.json](temp_0.0.json)