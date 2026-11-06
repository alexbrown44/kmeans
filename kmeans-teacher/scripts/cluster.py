#!/usr/bin/env python3
"""
Run a teaching-friendly K-means analysis on a CSV or Excel file.

What it does, in order:
  1. Loads the data and checks the chosen columns (numeric only; warns on IDs
     and categorical columns; fills missing values with the column median).
  2. Standardises the columns (z-scores) so no column dominates just because
     its numbers are bigger. Turn this off with --no-scale to see why it matters.
  3. Tries k = 2..kmax and reports inertia (Elbow Method) and silhouette score.
  4. Fits K-means with the chosen k (or the k with the best silhouette).
  5. Reports cluster sizes, centroids in original units, and which columns
     actually drove the split.
  6. Saves: labelled CSV, centroids CSV, charts (PNG), and results.json
     (everything the interactive artifact needs, including the iteration history).

Usage:
  python cluster.py --input customers.csv --features AnnualIncome SpendingScore TimeOnSite NumberOfVisits
  python cluster.py --input customers.csv --features AnnualIncome SpendingScore --k 5
  python cluster.py --input customers.csv --features AnnualIncome SpendingScore --no-scale
  python cluster.py --input customers.csv --list-columns
"""
import argparse
import json
import os
import sys
import warnings

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore", category=FutureWarning)

PALETTE = ["#2a78d6", "#e8743b", "#19a979", "#d64f8f", "#8a6bd6",
           "#c9a227", "#4fb3c9", "#7f7f7f", "#b0563b", "#5c8a3a"]


# ----------------------------------------------------------------- loading
def load(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xls", ".xlsm"):
        return pd.read_excel(path)
    # sniff the separator so semicolon or tab files also work
    return pd.read_csv(path, sep=None, engine="python")


def clean_numeric(series):
    """Turn '$52,000', '45%', ' 12 ' into numbers. Leaves real text as NaN."""
    if pd.api.types.is_numeric_dtype(series):
        return series.astype(float)
    s = (series.astype(str).str.strip()
         .str.replace(r"[$£€,%\s]", "", regex=True)
         .replace({"": np.nan, "nan": np.nan, "NaN": np.nan, "None": np.nan, "NA": np.nan}))
    return pd.to_numeric(s, errors="coerce")


def describe_columns(df):
    rows = []
    for c in df.columns:
        s = df[c]
        num = clean_numeric(s)
        share_num = num.notna().mean() if len(s) else 0
        nunique = s.nunique(dropna=True)
        if _looks_like_id(c) and nunique > 0.9 * max(len(s.dropna()), 1):
            kind = "identifier (skip)"
        elif share_num >= 0.9:
            kind = "numeric"
            if nunique == len(s.dropna()) and nunique > 20 and _looks_like_id(c):
                kind = "identifier (skip)"
            elif nunique <= 2:
                kind = "numeric but binary (usually skip)"
        else:
            kind = "categorical/text (not for vanilla K-means)"
        rows.append((c, kind, nunique, int(s.isna().sum())))
    return rows


def _looks_like_id(name):
    n = name.lower()
    return n.endswith("id") or n.startswith("id") or "number" == n or "code" in n


# ----------------------------------------------------------------- analysis
def prepare(df, features):
    notes = []
    lookup = {c.lower().replace(" ", ""): c for c in df.columns}
    resolved = []
    for f in features:
        if f not in df.columns and f.lower().replace(" ", "") in lookup:
            notes.append(f"Matched '{f}' to column '{lookup[f.lower().replace(' ', '')]}'.")
            f = lookup[f.lower().replace(" ", "")]
        resolved.append(f)
    features[:] = resolved
    missing = [f for f in features if f not in df.columns]
    if missing:
        close = {m: [c for c in df.columns if c.lower() == m.lower()] for m in missing}
        sys.exit(f"ERROR: columns not found: {missing}. Close matches: {close}. "
                 f"Available: {list(df.columns)}")

    X = pd.DataFrame(index=df.index)
    for f in features:
        num = clean_numeric(df[f])
        if num.notna().mean() < 0.9:
            sys.exit(
                f"ERROR: '{f}' is not numeric (only {num.notna().mean():.0%} of values are numbers).\n"
                "Vanilla K-means measures distance, and 'distance' between categories like "
                "'Fashion' and 'Books' isn't meaningful. Options: drop it from the features, "
                "use it afterwards to DESCRIBE the clusters, or use K-prototypes for mixed data.")
        if not pd.api.types.is_numeric_dtype(df[f]):
            notes.append(f"'{f}' was stored as text; converted to numbers (stripped $, %, commas).")
        n_bad = int(num.isna().sum())
        if n_bad:
            med = num.median()
            notes.append(f"'{f}': {n_bad} missing/unreadable values filled with the median ({med:,.2f}).")
            num = num.fillna(med)
        if num.nunique() <= 1:
            sys.exit(f"ERROR: '{f}' has a single value for every row; it cannot separate customers.")
        X[f] = num
    if len(X) < 10:
        sys.exit("ERROR: fewer than 10 rows; K-means needs more data to be meaningful.")
    return X, notes


def scan_k(Z, kmax, seed):
    ks = list(range(2, min(kmax, len(Z) - 1) + 1))
    inertias, sils = [], []
    sample = min(len(Z), 3000)  # silhouette is O(n^2); sample big files
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(Z)
        inertias.append(float(km.inertia_))
        sils.append(float(silhouette_score(Z, km.labels_, sample_size=sample, random_state=seed)))
    return ks, inertias, sils


def elbow_k(ks, inertias):
    """Point furthest from the line joining first and last inertia (the 'kink')."""
    x = np.array(ks, float); y = np.array(inertias, float)
    x_n = (x - x.min()) / (x.max() - x.min() or 1)
    y_n = (y - y.min()) / (y.max() - y.min() or 1)
    d = np.abs(y_n - (1 - x_n))  # distance from straight line (0,1)->(1,0)
    return int(ks[int(np.argmax(d))])


def silhouette_verdict(s):
    if s >= 0.5:
        return "strong structure: the clusters are well separated"
    if s >= 0.35:
        return "reasonable structure: real groups, with some overlap at the edges"
    if s >= 0.25:
        return "weak structure: groups overlap a lot; treat segments as rough tendencies"
    return "little or no real structure: K-means is drawing lines through a continuous cloud"


def replays(Z, k, final_labels, seed, tries=60):
    """Pick two random starting points to replay step by step:
    'good'    - a start that ends on the same answer as the final model
    'unlucky' - a start that gets stuck in a worse answer (higher inertia), if one exists.
    Real K-means guards against unlucky starts by running many starts (n_init) and keeping the best."""
    from sklearn.metrics import adjusted_rand_score
    good = unlucky = None
    worst_gap = 0.0
    best_inertia = None
    for t in range(tries):
        h = iteration_history(Z, k, seed + t)
        cents, labs = h[-1]
        inertia = float(((Z - cents[labs]) ** 2).sum())
        best_inertia = inertia if best_inertia is None else min(best_inertia, inertia)
        agree = adjusted_rand_score(final_labels, labs)
        if good is None and agree > 0.99 and len(h) >= 3:
            good = h
        if agree < 0.9:
            gap = inertia
            if gap > worst_gap:
                worst_gap, unlucky = gap, (h, inertia)
    if good is None:
        good = iteration_history(Z, k, seed)
    out = {"good": good, "unlucky": None, "unlucky_inertia_pct": None}
    if unlucky:
        final_inertia = float(((Z - np.array([Z[final_labels == j].mean(0) for j in range(k)])[final_labels]) ** 2).sum())
        out["unlucky"] = unlucky[0]
        out["unlucky_inertia_pct"] = round(100 * (unlucky[1] / final_inertia - 1), 1)
    return out


def iteration_history(Z, k, seed, max_steps=40):
    """Re-run Lloyd's algorithm one step at a time from a random start, for the stepper."""
    rng = np.random.default_rng(seed)
    centroids = Z[rng.choice(len(Z), k, replace=False)].copy()  # plain random init, visible to students
    history = []
    for _ in range(max_steps):
        d = ((Z[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
        labels = d.argmin(axis=1)
        history.append((centroids.copy(), labels.copy()))
        new = np.array([Z[labels == j].mean(axis=0) if (labels == j).any() else centroids[j]
                        for j in range(k)])
        if np.allclose(new, centroids):
            break
        centroids = new
    return history


def drivers(X, labels):
    """Share of each column's variance explained by cluster membership (eta-squared)."""
    out = {}
    for c in X.columns:
        total = ((X[c] - X[c].mean()) ** 2).sum()
        between = sum(((X[c][labels == g].mean() - X[c].mean()) ** 2) * (labels == g).sum()
                      for g in np.unique(labels))
        out[c] = float(between / total) if total else 0.0
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


# ----------------------------------------------------------------- charts
def chart_k(ks, inertias, sils, k_elbow, best_sil_k, chosen, path):
    """Each panel marks its own method's pick, so a disagreement is visible at a glance."""
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.4))
    ei = ks.index(k_elbow)
    ax[0].plot(ks, inertias, "o-", color=PALETTE[0])
    ax[0].plot(k_elbow, inertias[ei], "o", ms=14, mfc="none", mec=PALETTE[1], mew=2.5)
    ax[0].annotate(f"elbow: k={k_elbow}", (k_elbow, inertias[ei]), xytext=(14, 12),
                   textcoords="offset points", color=PALETTE[1], fontweight="bold")
    ax[0].set(title="Elbow Method: look for the bend", xlabel="k (number of groups)",
              ylabel="Spread inside groups (lower = tighter)")
    bi = ks.index(best_sil_k)
    ax[1].bar(ks, sils, color=[PALETTE[1] if k == best_sil_k else "#cfcfcf" for k in ks])
    ax[1].annotate(f"best: k={best_sil_k}", (best_sil_k, sils[bi]), xytext=(0, 6),
                   textcoords="offset points", ha="center", color=PALETTE[1], fontweight="bold")
    ax[1].set_ylim(min(0, min(sils)), max(sils) * 1.18)
    ax[1].set(title="Silhouette score: higher is better", xlabel="k (number of groups)",
              ylabel="How well separated (0 to 1)")
    for a in ax:
        a.spines[["top", "right"]].set_visible(False)
        a.set_xticks(ks)
    fig.suptitle(f"Elbow suggests k={k_elbow}; silhouette suggests k={best_sil_k}. "
                 f"This run uses k={chosen}.", fontsize=11)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


def chart_clusters(P, labels, C2, var_ratio, path):
    fig, ax = plt.subplots(figsize=(7.5, 6))
    for j in np.unique(labels):
        m = labels == j
        ax.scatter(P[m, 0], P[m, 1], s=14, alpha=0.6, color=PALETTE[j % 10], label=f"Cluster {j}")
    ax.scatter(C2[:, 0], C2[:, 1], s=260, marker="X", color="black", edgecolor="white", linewidth=1.5,
               label="Centroids")
    ax.set(title="Clusters (projected to 2D with PCA)",
           xlabel=f"PC1 ({var_ratio[0]:.0%} of variation)",
           ylabel=f"PC2 ({var_ratio[1]:.0%} of variation)" if len(var_ratio) > 1 else "")
    ax.legend(frameon=False, fontsize=8); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)


# ----------------------------------------------------------------- main
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True)
    p.add_argument("--features", nargs="+", help="numeric columns to cluster on")
    p.add_argument("--k", type=int, help="number of clusters (omit to let the data suggest one)")
    p.add_argument("--kmax", type=int, default=10)
    p.add_argument("--no-scale", action="store_true", help="skip standardisation (teaching demo)")
    p.add_argument("--log", nargs="+", help="log-transform these columns first (or 'all'); for skewed money columns")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--outdir", default="kmeans_output")
    p.add_argument("--describe", nargs="*", default=None,
                   help="extra columns (e.g. categorical) to profile per cluster; default: all non-feature columns")
    p.add_argument("--list-columns", action="store_true", help="show columns and their types, then exit")
    a = p.parse_args()

    df = load(a.input)
    df.columns = [str(c).strip() for c in df.columns]
    print(f"Loaded {len(df):,} rows x {df.shape[1]} columns from {a.input}\n")

    if a.list_columns or not a.features:
        print(f"{'Column':28} {'Type':45} {'Unique':>7} {'Missing':>8}")
        for c, kind, nu, miss in describe_columns(df):
            print(f"{c:28} {kind:45} {nu:>7} {miss:>8}")
        if not a.features:
            print("\nChoose numeric columns with --features to run the clustering.")
        return

    X, notes = prepare(df, a.features)
    for n in notes:
        print("NOTE:", n)
    if len(a.features) == 1:
        print("NOTE: clustering on a single column just slices it into ranges; two or more is more useful.")

    # W is the version of the data K-means actually sees (log-transformed where asked)
    W = X.copy()
    logged = [c for c in (a.features if a.log == ["all"] else (a.log or [])) if c in X.columns]
    for c in logged:
        if (X[c] < 0).any():
            sys.exit(f"ERROR: '{c}' has negative values, so a log transform isn't possible.")
        W[c] = np.log1p(X[c])
    if logged:
        print(f"Log transform applied to: {', '.join(logged)} (tames a few extreme values so they "
              "don't form their own cluster). Centroids for these columns are shown as cluster medians.")
    else:
        skewed = [c for c in X.columns if X[c].min() >= 0 and X[c].skew() > 2]
        if skewed:
            print(f"NOTE: heavily skewed columns (a few very large values): {', '.join(skewed)}. "
                  "Consider re-running with --log " + " ".join(skewed))

    scaler = None if a.no_scale else StandardScaler()
    Z = W.values if a.no_scale else scaler.fit_transform(W.values)
    print(f"Scaling: {'OFF (raw units; big-number columns will dominate)' if a.no_scale else 'ON (each column converted to z-scores)'}\n")

    ks, inertias, sils = scan_k(Z, a.kmax, a.seed)
    best_sil_k = ks[int(np.argmax(sils))]
    k_elbow = elbow_k(ks, inertias)
    k = a.k or best_sil_k
    print("Choosing k")
    print(f"{'k':>3} {'inertia':>14} {'silhouette':>11}")
    for kk, ine, s in zip(ks, inertias, sils):
        flag = "  <- best silhouette" if kk == best_sil_k else ""
        flag += "  <- elbow" if kk == k_elbow else ""
        print(f"{kk:>3} {ine:>14,.1f} {s:>11.3f}{flag}")
    print(f"\nElbow suggests k={k_elbow}; silhouette suggests k={best_sil_k}. Using k={k}"
          f"{' (your choice)' if a.k else ' (best silhouette)'}.")

    km = KMeans(n_clusters=k, n_init=10, random_state=a.seed).fit(Z)
    labels = km.labels_
    sil = float(silhouette_score(Z, labels, sample_size=min(len(Z), 3000), random_state=a.seed))
    fair_sil = None
    if a.no_scale:
        # A silhouette measured in raw units uses the same distorted ruler as the clustering,
        # so it flatters income-band clusters. Re-score the SAME clusters on standardised data.
        Zfair = StandardScaler().fit_transform(W.values)
        fair_sil = float(silhouette_score(Zfair, labels, sample_size=min(len(Z), 3000), random_state=a.seed))
        print(f"Silhouette at k={k} in raw units: {sil:.3f}  (misleading: measured with the same distorted ruler)")
        print(f"Same clusters scored on standardised data: {fair_sil:.3f} -> {silhouette_verdict(fair_sil)}\n")
    else:
        print(f"Silhouette at k={k}: {sil:.3f} -> {silhouette_verdict(sil)}")
        if sil < 0.25:
            print("WARNING: K-means always returns k groups, even when there are none. A score this low "
                  "means the 'segments' are arbitrary slices of one cloud. Do not build strategy on them.")
        print()

    # Centroids in original units: cluster means (medians for log-transformed columns)
    grouped = X.groupby(labels)
    cent_df = pd.DataFrame({c: (grouped[c].median() if c in logged else grouped[c].mean())
                            for c in a.features}).reset_index(drop=True)
    cent_df.insert(0, "Cluster", range(k))
    sizes = pd.Series(labels).value_counts().sort_index()
    cent_df.insert(1, "Size", sizes.values)
    cent_df.insert(2, "Share", (sizes.values / len(labels)).round(3))
    overall = X.mean()

    tiny = [int(j) for j, n in sizes.items() if n / len(labels) < 0.02]
    if tiny:
        print(f"WARNING: cluster(s) {tiny} hold under 2% of rows. These are usually outliers, not segments, "
              "and they can make the silhouette look better than the segmentation really is. "
              "Check for extreme values; a log transform (--log) often fixes this.\n")
    big = [int(j) for j, n in sizes.items() if n / len(labels) > 0.8]
    if big:
        print(f"WARNING: cluster {big} holds over 80% of rows, so this split separates a few unusual "
              "rows from everyone else rather than finding segments.\n")

    print("Cluster centroids (average customer in each cluster, original units)")
    print(cent_df.round(1).to_string(index=False))
    print(f"\nOverall averages: " + ", ".join(f"{c}={v:,.1f}" for c, v in overall.items()))
    # the profile below divides by this, so print it to let the profile be explained with real numbers
    spread = X.std()
    shown = [c for c in a.features if c not in logged]
    if shown:
        print("Typical spread (how far a customer usually sits from the average): "
              + ", ".join(f"{c}={spread[c]:,.1f}" for c in shown))

    drv = drivers(W, labels)
    print("\nWhat drove the split (share of each column's variation explained by the clusters)")
    for c, v in drv.items():
        print(f"  {c:22} {v:6.0%}  {'#' * int(round(v * 30))}")
    top = list(drv)[0]
    if a.no_scale and drv[top] > 0.7 and len(drv) > 1 and list(drv.values())[1] < 0.35:
        print(f"\nWARNING: '{top}' dominates. Without scaling, the column with the biggest numbers decides "
              "the clusters. Re-run without --no-scale to compare.")

    # relative profile: how far each centroid sits from average, in standard deviations
    rel = ((W.groupby(labels).mean() - W.mean()) / W.std()).reset_index(drop=True)[a.features]
    print("\nProfile: (cluster average - overall average) / typical spread, i.e. how many "
          "typical gaps above (+) or below (-) average")
    print(pd.concat([cent_df[["Cluster"]], rel.round(2)], axis=1).to_string(index=False))

    # profile extra columns (categoricals) per cluster
    describe_cols = a.describe if a.describe is not None else [
        c for c in df.columns if c not in a.features and not _looks_like_id(c)]
    profiles = {}
    for c in describe_cols:
        if c not in df.columns:
            continue
        if clean_numeric(df[c]).notna().mean() >= 0.9:
            profiles[c] = {int(j): round(float(clean_numeric(df[c])[labels == j].mean()), 2) for j in range(k)}
        else:
            profiles[c] = {int(j): df[c][labels == j].value_counts(normalize=True).round(2).head(3).to_dict()
                           for j in range(k)}
    if profiles:
        print("\nOther columns by cluster (not used for clustering, used to describe)")
        for c, by in profiles.items():
            print(f"  {c}:")
            for j, v in by.items():
                print(f"    Cluster {j}: {v}")

    # PCA projection for plotting
    n_comp = min(2, Z.shape[1])
    pca = PCA(n_components=n_comp, random_state=a.seed).fit(Z)
    P = pca.transform(Z)
    C2 = pca.transform(km.cluster_centers_)
    if n_comp == 1:
        P = np.c_[P, np.zeros(len(P))]; C2 = np.c_[C2, np.zeros(len(C2))]
    var_ratio = list(pca.explained_variance_ratio_)

    os.makedirs(a.outdir, exist_ok=True)
    out = df.copy(); out["Cluster"] = labels
    out.to_csv(os.path.join(a.outdir, "labelled_data.csv"), index=False)
    cent_df.round(3).to_csv(os.path.join(a.outdir, "centroids.csv"), index=False)
    chart_k(ks, inertias, sils, k_elbow, best_sil_k, k, os.path.join(a.outdir, "choose_k.png"))
    chart_clusters(P, labels, C2, var_ratio, os.path.join(a.outdir, "clusters_pca.png"))

    rp = replays(Z, k, labels, a.seed)

    def serialise(history):
        """Project replay centroids to the PCA plane and renumber clusters to match the final model."""
        from scipy.optimize import linear_sum_assignment
        last = history[-1][1]
        overlap = np.array([[np.sum((last == i) & (labels == j)) for j in range(k)] for i in range(k)])
        rows, cols = linear_sum_assignment(-overlap)
        remap = np.zeros(k, int); remap[rows] = cols
        steps = []
        for cs, ls in history:
            xy = pca.transform(cs)
            if n_comp == 1:
                xy = np.c_[xy, np.zeros(len(xy))]
            ordered = np.zeros_like(xy); ordered[remap] = xy
            steps.append({"centroids": np.round(ordered, 4).tolist(), "labels": remap[ls].tolist()})
        return steps

    id_col = next((c for c in df.columns if _looks_like_id(c)), None)
    results = {
        "source": os.path.basename(a.input), "rows": len(df), "features": a.features,
        "scaled": not a.no_scale, "k": k, "seed": a.seed,
        "k_scan": {"ks": ks, "inertia": inertias, "silhouette": sils,
                   "elbow_k": k_elbow, "best_silhouette_k": best_sil_k},
        "silhouette": sil, "silhouette_fair": fair_sil,
        "silhouette_verdict": silhouette_verdict(fair_sil if fair_sil is not None else sil),
        "pca_variance": var_ratio,
        "points": [{"x": round(float(P[i, 0]), 4), "y": round(float(P[i, 1]), 4), "c": int(labels[i]),
                    "id": str(df[id_col].iloc[i]) if id_col else str(i),
                    "v": {f: float(X[f].iloc[i]) for f in a.features}} for i in range(len(df))],
        "centroids": [{"cluster": int(r.Cluster), "size": int(r.Size), "share": float(r.Share),
                       "values": {f: round(float(r[f]), 2) for f in a.features},
                       "z": {f: round(float(rel.iloc[i][f]), 2) for f in a.features},
                       "xy": [round(float(C2[i, 0]), 4), round(float(C2[i, 1]), 4)]}
                      for i, r in cent_df.iterrows()],
        "overall_means": {f: round(float(v), 2) for f, v in overall.items()},
        "overall_spread": {f: round(float(spread[f]), 2) for f in shown},
        "drivers": drv,
        "profiles": profiles,
        "iterations": serialise(rp["good"]),
        "iterations_unlucky": serialise(rp["unlucky"]) if rp["unlucky"] else None,
        "unlucky_worse_pct": rp["unlucky_inertia_pct"],
        "notes": notes,
    }
    with open(os.path.join(a.outdir, "results.json"), "w") as f:
        json.dump(results, f)

    print(f"\nSaved to {a.outdir}/: labelled_data.csv, centroids.csv, choose_k.png, clusters_pca.png, results.json")
    print(f"Step-by-step replay: converges in {len(rp['good'])} steps to the final answer.")
    if rp["unlucky"]:
        print(f"Unlucky-start replay: gets stuck after {len(rp['unlucky'])} steps in an answer "
              f"{rp['unlucky_inertia_pct']}% worse. This is why K-means is run from many starts (n_init=10).")


if __name__ == "__main__":
    main()
