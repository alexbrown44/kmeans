#!/usr/bin/env python3
"""
Build the interactive K-means explorer: one self-contained HTML page.

Takes the results.json written by cluster.py and injects it into
assets/explorer_template.html. The page needs no internet and no other files,
so it works opened straight from disk or published as an artifact.

Usage:
  python build_explorer.py --results out/results.json --out kmeans_explorer.html
  python build_explorer.py --results out/results.json --out kmeans_explorer.html \
      --title "Online store customers" --names "High-value loyalists" "Bargain hunters" ...

Uses only the Python standard library.
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "explorer_template.html")
PLACEHOLDER = "__KMEANS_DATA__"
REQUIRED = ["k", "features", "points", "centroids", "k_scan", "iterations", "silhouette"]


def clean(x):
    """Swap NaN/inf for None: Python's json writes NaN, but browsers can't parse it."""
    if isinstance(x, float) and not math.isfinite(x):
        return None
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, list):
        return [clean(v) for v in x]
    return x


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--results", required=True, help="results.json from cluster.py")
    p.add_argument("--out", default="kmeans_explorer.html")
    p.add_argument("--title", help="heading for the page (default: 'K-means explorer')")
    p.add_argument("--names", nargs="+", help="cluster names in cluster order (0, 1, 2, ...)")
    p.add_argument("--template", default=TEMPLATE)
    a = p.parse_args()

    try:
        with open(a.results) as f:
            results = json.load(f)
    except FileNotFoundError:
        sys.exit(f"ERROR: {a.results} not found. Run cluster.py first; it writes results.json to its --outdir.")
    missing = [key for key in REQUIRED if key not in results]
    if missing:
        sys.exit(f"ERROR: {a.results} is missing {missing}. Is it from cluster.py?")

    k = results["k"]
    if a.names and len(a.names) != k:
        sys.exit(f"ERROR: got {len(a.names)} names for {k} clusters. Give one name per cluster, in order.")

    with open(a.template, encoding="utf-8") as f:
        template = f.read()
    if PLACEHOLDER not in template:
        sys.exit(f"ERROR: {a.template} has no {PLACEHOLDER} placeholder.")

    payload = {"results": clean(results), "names": a.names, "title": a.title}
    # '</' would close the <script> tag early if a column name or ID contains it
    data = json.dumps(payload, allow_nan=False, separators=(",", ":")).replace("</", "<\\/")
    html = template.replace(PLACEHOLDER, data)

    with open(a.out, "w", encoding="utf-8") as f:
        f.write(html)
    size_kb = os.path.getsize(a.out) / 1024
    print(f"Saved {a.out} ({size_kb:,.0f} KB): {results['rows']:,} rows, k={k}, "
          f"{len(results['iterations'])} replay steps"
          f"{', unlucky replay included' if results.get('iterations_unlucky') else ''}.")
    if size_kb > 15000:
        print("WARNING: over 15 MB. Artifacts have a size limit; sample the rows before clustering.")


if __name__ == "__main__":
    main()
