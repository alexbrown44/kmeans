# Plain-English explanations

Each concept has a **simple** version (the default, for newcomers and for demos)
and a **deeper** version (only for users who are clearly technical or ask for it).
Adapt the wording to the user's own data.

## House rules for the simple versions

- **Plain idea first, name second.** Explain the idea in everyday words, then give
  the technical name once, if it's needed at all: "the middle of each group, which
  statisticians call the centroid". After that, prefer the plain word.
- **One analogy per concept**, from everyday life. The ones below are tested; reuse them.
- **Never quote a number on its own.** Every number gets a short reminder of what it
  means and what counts as good. See "Reading the numbers" at the end.
- **Never quote a number before its idea has been explained.** A reminder can't
  rescue a score the audience has never met. Describe what happened in plain
  words instead.
- **Words to avoid in simple mode** unless the user uses them first: inertia,
  z-score, standard deviation, Euclidean, variance, eta-squared, PCA, principal
  component, local minimum, convergence, algorithm. Use the plain phrases in
  brackets throughout this file instead.

## What K-means does
**Simple:** Think of a school dance where nobody knows anyone. You drop k hosts
into the room at random. Everyone walks to their nearest host. Then each host
moves to the middle of their crowd. People look again and switch to whichever
host is now closest. Repeat until nobody moves. Each crowd is a **group** (a
cluster); each host ends up standing at the **middle of the group** (the centroid).
The number of hosts is **k**, and you choose it.

**Deeper:** K-means (Lloyd's algorithm) minimises the within-cluster sum of
squared distances (inertia). It alternates an assignment step (each point to its
nearest centroid) and an update step (each centroid to the mean of its points).
Each step can only lower inertia, so it always converges, but to a local
minimum that depends on the starting centroids. That's why it's run from several
starts (n_init) and the best kept. Initialisation by k-means++ spreads starting
centroids apart to make bad starts rarer.

## Nobody tells it the answer (unsupervised learning)
**Simple:** It's like sorting a box of mixed buttons without being told the
categories. You might sort by colour, size or number of holes, and each is a
fair answer. K-means sorts on its own, which is useful when you don't know your
segments yet. The risk: it will always come back with a sort, even when the
buttons are all basically the same.

**Deeper:** There's no target variable and no ground truth, so there's no
accuracy score. Evaluation relies on internal measures (silhouette, inertia),
stability across samples, and whether the segments are actionable.

## Why scaling matters
**Simple:** K-means decides who's alike by measuring how far apart two customers
are. Without scaling, it's like comparing two people by their height in
millimetres and their age in years: the height numbers are so much bigger that
age barely counts. Income here is in tens of thousands; spending score stops at
100. So income decides everything. Scaling puts every column in the same units:
"how unusual is this customer for this column?" Then every column gets a fair say.

Show it with the unscaled groups, not with scores: "The five groups have average
incomes of $41k, $53k, $75k, $114k and $140k, but almost the same spending and
visits. K-means hasn't found kinds of customer; it has sorted people by income."
No silhouette, percentages or "centroids" here: none of them has been
introduced yet.

**Deeper:** Standardisation converts each feature to z-scores (subtract the
mean, divide by the standard deviation), so each contributes comparable
variance to Euclidean distance. The choice of scaling is itself a weighting
decision; standardising says "every column matters equally". If one column
should matter more, that's a deliberate choice, not a default.

## Choosing k: the elbow
**Simple:** Think of hiring staff for a shop. The first few hires make a big
difference; after a while, each extra person adds less and less. The elbow chart
shows the same thing for groups: each extra group makes the groups tighter, but
the gains shrink. The **bend in the curve** (the "elbow") is where another group
stops being worth it. It's often a gentle bend, so it's a judgment call.

**Deeper:** Inertia decreases monotonically with k, so its minimum is useless.
The elbow is the point of diminishing returns. On real data it's often a soft
curve, and different people will read it differently. The script estimates it
as the point furthest from the straight line joining the first and last values.

## Choosing k: the silhouette score
**Simple:** Picture each customer at a party, asking: "Am I closer to my own
group, or to the next group over?" If they're right in the middle of their own
group, they score near 1. If they're standing in the doorway between two groups,
they score near 0. The silhouette score is the average across everyone, so it
tells you **how clearly the groups stand apart**.

**Deeper:** For point i, s(i) = (b - a) / max(a, b), where a is the mean
distance to points in its own cluster and b the mean distance to points in the
nearest other cluster. The mean silhouette rewards compact, separated clusters.
It favours convex, similar-sized clusters, as K-means does, so it can't detect
when K-means is the wrong tool.

## When the elbow and silhouette disagree
**Simple:** They answer different questions. The silhouette asks "where are the
cleanest borders?"; the elbow asks "where does another group stop paying off?"
When they disagree, neither is wrong. **The business question decides.** Say
plainly which k each one points to, then ask which split the user can act on.

## The middle of each group (centroids)
**Simple:** The middle of a group is its "typical customer": the average age,
average income and so on of everyone in it. Put it next to the average customer
overall and the differences jump out: "younger than average, much lower income,
but spends a lot".

**Deeper:** Centroids are computed in scaled space and transformed back to
original units for reading. The z-score profile (centroid minus overall mean,
divided by standard deviation) shows distinctiveness on a common scale: about
+/-1 is very distinctive.

## How far above or below average (the profile)
**Simple:** Instead of raw numbers, the profile says how far each group sits from
the typical customer, on one shared ruler. Think of it as "how unusual": **0** is
completely normal, **+1** is clearly above normal, **−1** clearly below. Anything
beyond ±1 is a defining trait of that group.

## What drove the split
**Simple:** For each column, how much did it matter in sorting people into
groups? Imagine sorting a class into teams and then asking: "If I only knew
someone's team, how well could I guess their height?" A high percentage means
that column strongly separates the groups; a low one means it barely mattered.

**Deeper:** This is eta-squared: between-cluster sum of squares divided by
total sum of squares, per feature. It shows which features the partition
actually uses. In unscaled data, it exposes the dominant-feature problem.

## The cluster map (PCA plot)
**Simple:** We have five columns, but a screen is flat. The map is like a
shadow of a 3D object on a wall: it keeps the most important shape, but some
detail is lost. Dots close together are similar customers. Two groups that
overlap on the map might still be separate in reality, just as two objects can
cast overlapping shadows.

**Deeper:** PCA projects standardised data onto the top principal components.
The axis labels show the share of variance each captures. If the two
components capture under ~60%, treat the picture as a rough sketch.

## The unlucky start
**Simple:** Back to the dance: if two hosts happen to start in the same corner,
they split one crowd between them, while another crowd across the room has to
share a single host. Nobody has a reason to move, so it gets stuck in a worse
answer. The fix is simple: run it from many different starts and keep the best.
The real run does this 10 times.

**Deeper:** Lloyd's algorithm converges to a local optimum. sklearn's default
k-means++ plus n_init=10 runs make poor solutions unlikely, not impossible.
Large differences in inertia between runs indicate an unstable solution.

## When K-means is the wrong tool
- Clusters that aren't roughly round blobs (long chains, rings): use DBSCAN or
  hierarchical clustering.
- Very different cluster sizes or densities: K-means tends to split big groups
  and merge small ones; consider Gaussian mixture models.
- Mostly categorical data: K-modes / K-prototypes.
- Heavy outliers: they drag centroids; transform, cap or remove them first.

## Reading the numbers

Attach the matching reminder every time you quote one of these. Keep it to a few
words in brackets, then say what it means for this data.

| Number | Reminder to attach |
|---|---|
| Silhouette score | "on a 0-to-1 scale; above 0.5 is strong, 0.35-0.5 is decent, below 0.25 means little real structure" |
| Fair silhouette of the unscaled run | Only after the silhouette is explained, never in the scaling step. Recall the moment, then compare: "the income-band groups from our first try, scored with every column counting equally, get 0.04, almost no structure; our groups now get 0.47". Skip the raw-units score with beginners; it needs too much explaining. |
| What drove the split (%) | "how much that column mattered in forming the groups; near 100% means it decided them, near 0% means it barely counted" |
| Profile (+1.2, −0.8 …) | "how unusual the group is on that column; 0 is average, beyond ±1 is a defining trait" |
| Group size / share | "how many customers, and what share of all of them; under about 5% is usually too small for its own campaign" |
| Elbow chart values | "how spread out the groups are; lower is tighter, and only the shape of the curve matters, not the numbers" |
| Unlucky start "% worse" | "how much more spread out the groups are than in the best answer" |
| Chart axes ("PC1, 48% of variation") | "the map keeps about half of the differences between customers; treat it as a sketch" |

**Example, without reminder:** "Silhouette is 0.47."
**Example, with reminder:** "The silhouette is 0.47. On a 0-to-1 scale where above
0.5 is strong, that's decent: real groups, with some customers near the borders."
