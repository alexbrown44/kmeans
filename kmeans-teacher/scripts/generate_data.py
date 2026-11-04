#!/usr/bin/env python3
"""
Generate a synthetic e-commerce customer dataset for teaching K-means.

Two modes:
  clustered  - customers drawn from five hidden behavioural segments
               (the "realistic" dataset used for the main lesson)
  noise      - the same columns, but every value drawn independently,
               so there are NO real segments (used for the "noise trap" lesson)

The random seed is fixed, so every run produces exactly the same data.
That keeps live demos and student results reproducible.

Usage:
  python generate_data.py                      # clustered, 800 rows -> customers.csv
  python generate_data.py --mode noise         # noise version -> customers_noise.csv
  python generate_data.py --n 1000 --seed 7 --out my_data.csv
"""
import argparse

import numpy as np
import pandas as pd

CATEGORIES = ["Electronics", "Fashion", "Home", "Books", "Sports"]

# Five hidden segments. Each has a typical value (mean) and spread (sd) per feature.
# These are the "answer key" that K-means should rediscover on scaled data.
SEGMENTS = {
    "High-value loyalists": dict(
        share=0.18, age=(42, 8), income=(115_000, 18_000), spend=(82, 7),
        time=(14, 3), visits=(14, 3),
        gender=[0.48, 0.48, 0.04], category=[0.35, 0.20, 0.25, 0.05, 0.15]),
    "Bargain hunters": dict(
        share=0.24, age=(38, 10), income=(52_000, 12_000), spend=(30, 8),
        time=(24, 4), visits=(16, 3),
        gender=[0.42, 0.53, 0.05], category=[0.15, 0.35, 0.30, 0.10, 0.10]),
    "Casual browsers": dict(
        share=0.26, age=(48, 12), income=(60_000, 15_000), spend=(22, 8),
        time=(5, 2), visits=(3, 1.5),
        gender=[0.50, 0.46, 0.04], category=[0.15, 0.15, 0.20, 0.35, 0.15]),
    "Young impulse buyers": dict(
        share=0.18, age=(24, 4), income=(38_000, 9_000), spend=(74, 9),
        time=(11, 3), visits=(10, 3),
        gender=[0.40, 0.54, 0.06], category=[0.30, 0.40, 0.05, 0.05, 0.20]),
    "Affluent but disengaged": dict(
        share=0.14, age=(55, 8), income=(125_000, 20_000), spend=(18, 7),
        time=(4, 1.5), visits=(2, 1),
        gender=[0.55, 0.42, 0.03], category=[0.25, 0.10, 0.35, 0.20, 0.10]),
}

GENDERS = ["Male", "Female", "Other"]


def _clip_round(values, lo, hi, decimals=0):
    return np.round(np.clip(values, lo, hi), decimals)


def make_clustered(n, rng):
    names = list(SEGMENTS)
    shares = np.array([SEGMENTS[s]["share"] for s in names])
    counts = np.floor(shares / shares.sum() * n).astype(int)
    counts[0] += n - counts.sum()  # make the total exactly n

    frames = []
    for name, count in zip(names, counts):
        s = SEGMENTS[name]
        frames.append(pd.DataFrame({
            "Age": _clip_round(rng.normal(*s["age"], count), 18, 70),
            "Gender": rng.choice(GENDERS, count, p=s["gender"]),
            "AnnualIncome": _clip_round(rng.normal(*s["income"], count), 15_000, 250_000, -2),
            "SpendingScore": _clip_round(rng.normal(*s["spend"], count), 1, 100),
            "TimeOnSite": _clip_round(rng.normal(*s["time"], count), 0.5, 60, 1),
            "NumberOfVisits": _clip_round(rng.normal(*s["visits"], count), 1, 40),
            "PreferredCategory": rng.choice(CATEGORIES, count, p=s["category"]),
            "_TrueSegment": name,  # hidden answer key, dropped unless --keep-truth
        }))
    df = pd.concat(frames, ignore_index=True)
    return df.sample(frac=1, random_state=rng.integers(1_000_000)).reset_index(drop=True)


def make_noise(n, rng):
    """Same columns and similar ranges, but no structure at all."""
    return pd.DataFrame({
        "Age": _clip_round(rng.uniform(18, 70, n), 18, 70),
        "Gender": rng.choice(GENDERS, n, p=[0.47, 0.49, 0.04]),
        "AnnualIncome": _clip_round(rng.uniform(20_000, 150_000, n), 15_000, 250_000, -2),
        "SpendingScore": _clip_round(rng.uniform(1, 100, n), 1, 100),
        "TimeOnSite": _clip_round(rng.uniform(1, 30, n), 0.5, 60, 1),
        "NumberOfVisits": _clip_round(rng.uniform(1, 20, n), 1, 40),
        "PreferredCategory": rng.choice(CATEGORIES, n),
    })


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mode", choices=["clustered", "noise"], default="clustered")
    p.add_argument("--n", type=int, default=800, help="number of customers (default 800)")
    p.add_argument("--seed", type=int, default=42, help="random seed (default 42)")
    p.add_argument("--out", help="output CSV path")
    p.add_argument("--keep-truth", action="store_true",
                   help="keep the hidden _TrueSegment column (for instructor checks only)")
    a = p.parse_args()

    rng = np.random.default_rng(a.seed)
    df = make_clustered(a.n, rng) if a.mode == "clustered" else make_noise(a.n, rng)
    if "_TrueSegment" in df and not a.keep_truth:
        df = df.drop(columns="_TrueSegment")

    df.insert(0, "CustomerID", [f"C{i:04d}" for i in range(1, len(df) + 1)])
    for col in ["Age", "AnnualIncome", "SpendingScore", "NumberOfVisits"]:
        df[col] = df[col].astype(int)

    out = a.out or ("customers.csv" if a.mode == "clustered" else "customers_noise.csv")
    df.to_csv(out, index=False)

    print(f"Saved {len(df)} customers ({a.mode} mode, seed {a.seed}) to {out}")
    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))
    print("\nNumeric summary:")
    print(df.describe().round(1).to_string())


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:  # output piped into head etc.; the file is already saved
        pass
