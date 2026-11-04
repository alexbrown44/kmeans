# Bundled data

## wholesale_customers.csv (real data)
440 clients of a wholesale distributor in Portugal, with annual spending (in monetary
units) on six product categories, plus Channel and Region.

- Source: UCI Machine Learning Repository, "Wholesale customers" (dataset 292).
  Margarida Cardoso (2013). https://doi.org/10.24432/C5030X
- Licence: CC BY 4.0
- Changes made here: added ClientID; Channel 1/2 -> "Hotel/Restaurant/Cafe"/"Retail";
  Region 1/2/3 -> "Lisbon"/"Oporto"/"Other"; renamed "Delicassen" to "Delicatessen".

Cluster on the six spending columns with `--log all` (spending is heavily skewed).
Use Channel and Region only to describe the clusters afterwards.

## Synthetic data
Not stored here: generate it with `scripts/generate_data.py` (seeded, so it is
identical every time).
