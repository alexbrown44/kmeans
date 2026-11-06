# What is this?

**K-means Teacher** is a skill you add to Claude. Once it's installed, Claude can run
a real K-means analysis, on sample data or on your own spreadsheet, and explain every
step in plain English as it goes. You end up with a working customer segmentation
*and* an understanding of how it was made and when to trust it.

No coding needed. You type requests; Claude runs the analysis.

---

## K-means in one minute

Imagine 800 customers, each described by a few numbers: age, income, how much they
spend, how often they visit. You suspect there are different *kinds* of customer in
there, but nobody has labelled them.

K-means finds those groups for you. You choose how many groups you want (that number
is the **k**), and it repeats two simple steps:

1. **Assign:** every customer joins the group whose centre is nearest.
2. **Update:** each group's centre moves to the middle of its members.

It repeats until nobody switches group. The result is k groups of customers who are
similar to each other and different from the other groups. Each group's centre, the
**centroid**, describes its typical member: "age 24, low income, but spends a lot".

That's the whole algorithm. The skill's interactive explorer lets you watch it happen
step by step.

## Why it's so widely used

K-means is one of the oldest and most widely used ways to find groups in data. The
idea dates back to the 1950s, and it is still a standard first tool today because it is:

- **Simple:** two steps, easy to explain to a non-technical audience.
- **Fast:** it handles hundreds of thousands of rows on an ordinary computer.
- **Easy to act on:** every cluster has a "typical member" you can describe, name and
  build a plan around.
- **Everywhere:** it's built into Python, R and most analytics and data-science tools.

**Where businesses use it:**
- **Customer segmentation:** different campaigns, offers or service levels for different groups.
- **Product and store grouping:** stores that sell alike, products that are bought alike.
- **Pricing and risk:** grouping customers or accounts by behaviour before setting terms.
- **Operations:** grouping delivery locations, or similar support tickets.

### What it can't do

Knowing the limits is half the skill:

- **It always returns k groups, even when there are none.** Feed it random noise and it
  will still hand you neat-looking segments. The silhouette score (see below) is how
  you check.
- **You choose k.** The data can suggest a number, but the final choice is a business
  decision: more groups means finer detail, fewer means simpler action.
- **Numbers only.** It measures distance, and there's no distance between "Books" and
  "Fashion". Text columns are used afterwards to *describe* the groups instead.
- **Scale matters.** Without adjustment, a column in the tens of thousands (income)
  drowns out one that stops at 100 (a score). The skill handles this for you and shows why.

**The silhouette score** runs from −1 to 1 and measures how well separated the groups are:

| Score | What it means |
|---|---|
| 0.50+ | Strong, clearly separate groups |
| 0.35–0.50 | Real groups, some overlap |
| 0.25–0.35 | Weak; treat the groups as tendencies |
| Below 0.25 | Little or no real structure; don't build strategy on it |

Real business data usually scores 0.2–0.4. That's normal, not a mistake.

---

## Use 1: as a demo

Good for teaching a class, explaining segmentation to a team, or learning it yourself.

The skill comes with **synthetic customer data**: 800 online shoppers with five kinds
of customer mixed in. That's deliberate: it's like testing a metal detector by
burying a coin first. We know the answer; K-means only gets the numbers. If it
finds the types, you know the tool works before you trust it on real data, where
nobody knows the answer. The demo walks through the lessons that matter most:

1. **The data:** which columns to use, and why IDs and text columns are left out.
2. **Scaling:** a live before-and-after showing one column taking over.
3. **Choosing k:** the two standard methods disagree (4 vs 5), and the business
   question settles it.
4. **The segments:** five named groups, then the reveal that they are the five hidden ones.
5. **Watching it run:** a step-by-step replay, plus an "unlucky start" that ends 85% worse.
6. **Campaigns:** one per segment, with a reality check.
7. **The noise trap:** K-means "finds" segments in pure randomness, and the score gives it away.

**To start**, open a new chat and type:

> I'm running a classroom demo. Use the synthetic e-commerce customer data, in classroom demo mode.

In demo mode Claude keeps each answer short, does one step at a time, and always
stops to let you choose k. For a timed 15-minute version with exact prompts, see the
[run sheet](RUN_SHEET.md).

**No time to install?** The [interactive explorer](https://claude.ai/artifact/KH7dmKcYzkBTdKz1MRDdzk)
shows a finished demo in any browser.

**Follow-up lesson:** the skill also includes real data, 440 clients of a Portuguese food
distributor. It's messier and scores lower (0.29), yet K-means still separates restaurants
and cafés from retailers using spending alone. Ask: *"Does this work on real data? Try the
wholesale customers file."*

## Use 2: on your own data

Upload a CSV or Excel file and type something like:

> Segment these customers with K-means.

**What works well:** one row per customer (or store, product, account), with numeric
columns that describe behaviour, such as spend, frequency, recency, basket size or
tenure. Text columns such as region or channel are fine to include. Claude won't
cluster on them, but uses them to describe each segment afterwards.

**What the skill handles for you:**
- Numbers stored as text, like `$52,000` or `45%`, are converted.
- Missing values are filled with the column's typical value, and Claude tells you how many.
- ID columns are spotted and skipped.
- Very skewed columns, where a few huge customers would form their own "segment",
  are flagged, with a fix.
- Columns are put on the same scale before clustering.

**What you get:**
- A plain-English summary of each segment, with suggested names
- An honest verdict on how far to trust the result
- Charts for choosing k and for the cluster map
- An interactive explorer page
- **Your data with a segment label on every row** (a CSV, ready for Excel), plus a table of
  segment averages
- One campaign idea per segment, with a reality check

**Questions worth asking along the way:**
- *"Which columns should I use?"*
- *"Why did you recommend this number of segments?"*
- *"What would change with one more segment?"*
- *"How much should I trust this?"*
- *"Show me the code."* (Claude explains in plain language unless you ask.)

**Good to know:**
- **Results are repeatable.** The same data and settings always give the same answer.
- **Large files** (over about 50,000 rows) are slower. Claude will sample the rows to choose k.
- **Your data goes to Claude.** Before uploading customer data, check that your
  organisation allows it, and remove names, emails and other personal details you don't need.
  The analysis never needs them.

---

## Getting started

See the [README](README.md) to download the skill and install it in about two minutes.
It works on every Claude plan, with code execution turned on.
