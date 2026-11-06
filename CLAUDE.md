# K-means teaching skill - project notes

Alex is building a Claude Skill that teaches K-means clustering, for a live
online class on **Monday 9 November 2026** (10-15 minute demo slot) to
business-school students. Students then get this repo to install the skill
themselves. This file is the handoff from the build session in Claude chat.

## What this repo contains
- `kmeans-teacher/` - the skill (this folder gets zipped and uploaded to Claude)
  - `SKILL.md` - the teaching flow Claude follows
  - `scripts/generate_data.py` - synthetic customer data, `--mode clustered|noise`, seed 42
  - `scripts/cluster.py` - cleaning, scaling, choosing k, K-means, charts, `results.json`
  - `references/explanations.md` - plain-English explanations, simple and deeper
  - `data/wholesale_customers.csv` - real data (UCI Wholesale customers, CC BY 4.0)

## Decisions already made (don't reopen without asking Alex)
- Skill + artifact, no standalone app.
- All numbers come from the bundled seeded scripts, never improvised code.
- Narrative first; code shown only on request.
- Synthetic data: 800 customers, five hidden segments (High-value loyalists,
  Bargain hunters, Casual browsers, Young impulse buyers, Affluent but disengaged).
- Real data: UCI Wholesale customers, clustered with `--log all`.

## Tested results (Day 1, all passing)
Synthetic, features Age AnnualIncome SpendingScore TimeOnSite NumberOfVisits:
- Scaled k=5: recovers all five segments (95-100% purity), silhouette 0.473.
- Silhouette picks k=4, elbow picks k=5. At k=4 "Casual browsers" and
  "Affluent but disengaged" merge (can't spend vs won't spend). Scripted demo beat.
- Unscaled: AnnualIncome drives 96% of the split; fair silhouette 0.041 (vs 0.473).
- Noise mode: silhouette ~0.15 flat for every k; script warns.
- Replays: clean replay ends exactly on the final answer (6 steps at k=5);
  "unlucky start" replay ends 85% worse.
- Reproducible: identical output on repeated runs.
Real data (wholesale): raw silhouette 0.548 but 89% in one cluster + 2 outliers
(script warns); with `--log all --k 2`, silhouette 0.29 and clusters separate
97% hotels/restaurants/cafes from mostly retail without using the Channel column.
Robustness: semicolon CSV, Excel, $ and commas, missing values, wrong-case
column names, categorical and ID columns all handled with clear messages.

If you change `cluster.py` or `generate_data.py`, re-run these checks and
confirm the numbers above still hold.

Day 3 (2026-11-05): `chart_k()` in cluster.py changed so each panel of
choose_k.png marks its own method's pick (the old one marked the chosen k on
both, so both showed 4 before k was chosen). Drawing only; no numbers changed.
It only compiles here (pandas is blocked on Alex's PC), so check that
choose_k.png renders on the next Claude-chat rehearsal.

Day 4 (2026-11-06): cluster.py also prints a "Typical spread" line (std of
each non-logged column) and writes `overall_spread` to results.json, so the
profile ("how unusual") numbers can be explained with a worked example.
Print-only; no existing numbers changed. Also compile-checked only.

Day 4, later: the chart_k fix is confirmed rendering in Claude chat (each
panel labels its own pick). Its title now says "Which to use is a business
decision." when no --k is given, instead of announcing the silhouette
fallback as "This run uses k=4". Compile-checked only.

## Still to do (Day 2 and 3)
1. DONE (Day 2), tested on a schema-faithful mock only: pandas is blocked by
   Windows Application Control on Alex's PC, so cluster.py can't run there.
   First real test is item 2. Spec was:
   **`kmeans-teacher/scripts/build_explorer.py`** plus
   **`kmeans-teacher/assets/explorer_template.html`**. SKILL.md Step 6 already
   calls: `python scripts/build_explorer.py --results out/results.json --out kmeans_explorer.html`.
   It injects results.json into the template to make ONE self-contained HTML page:
   - cluster map (PCA scatter, coloured by cluster, centroids marked)
   - step-by-step replay with Step / Play / Reset, using `iterations`
   - "unlucky start" toggle using `iterations_unlucky` and `unlucky_worse_pct`
   - elbow and silhouette charts from `k_scan`
   - centroid profile table (`centroids[].values` and `.z`), sizes, drivers
   - must work offline as a file AND as a published artifact; no external data
   - mobile width OK, readable on a shared screen (big type)
2. **Public no-install demo link**: build the explorer on the synthetic k=5
   results and publish it as a public artifact. This is the link most students
   will actually use, so polish matters.
   DONE (Day 2): https://claude.ai/artifact/KH7dmKcYzkBTdKz1MRDdzk (public,
   real synthetic k=5 run, checked 2026-11-04). It predates the CSV-button
   removal, so it still shows a dead Download CSV button. Don't unpublish it:
   the README links to it.
3. **README.md** for students: DONE (Day 2), demo link added. Install steps checked
   against support.claude.com article 12512180 on 2026-11-04.
   The README links to `kmeans-teacher.zip` in the repo root. **Rebuild and
   commit that zip whenever anything in `kmeans-teacher/` changes**, or
   students download a stale skill.
4. DONE (Day 2): `RUN_SHEET.md`. Expected numbers taken from the first real
   Claude-chat run. Uses the published demo link for the replay instead of
   building the explorer live. Unverified until rehearsal: that the new
   one-beat-per-reply rule holds. Spec was:
   **Run sheet** for Alex: the exact prompts to type in class, in order, with
   what should appear after each. Fit 10-15 minutes. Recommended cut:
   data -> scaling beat -> choosing k (4 vs 5) -> segments and campaigns ->
   noise trap. Real data gets one sentence; it's homework in the repo.
5. **Rehearsals in Claude chat (not Claude Code)**: install the zipped skill in
   Alex's Claude account and run the run sheet three times. Sunday = freeze.

## Working style
Alex wants blunt, direct advice: push back, flag risks, no flattery.
