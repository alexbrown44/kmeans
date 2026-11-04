# Plain-English explanations

Each concept has a **simple** version (for newcomers) and a **deeper** version
(for technical users). Adapt the wording to the user's own data.

## What K-means does
**Simple:** Imagine you need to set up k shops in a city so that every customer
is as close as possible to a shop. You put the shops down somewhere, each
customer goes to their nearest shop, then each shop moves to the middle of its
customers. Repeat until nobody switches shop. The shops are the *centroids*;
each shop's customers are a *cluster*.

**Deeper:** K-means (Lloyd's algorithm) minimises the within-cluster sum of
squared distances (inertia). It alternates an assignment step (each point to its
nearest centroid) and an update step (each centroid to the mean of its points).
Each step can only lower inertia, so it always converges, but to a local
minimum that depends on the starting centroids. That's why it's run from several
starts (n_init) and the best kept. Initialisation by k-means++ spreads starting
centroids apart to make bad starts rarer.

## Unsupervised learning
**Simple:** Nobody tells K-means what the groups are. It finds groups on its own.
That's useful when you don't know your segments yet, and risky because it will
always find *something*.

**Deeper:** There's no target variable and no ground truth, so there's no
accuracy score. Evaluation relies on internal measures (silhouette, inertia),
stability across samples, and whether the segments are actionable.

## Why scaling matters
**Simple:** K-means decides who's similar by distance. A $10,000 income gap
counts as 10,000; a 30-point spending gap counts as 30. So without scaling,
income decides everything. Scaling puts every column on the same footing:
"how unusual is this value for this column?"

**Deeper:** Standardisation converts each feature to z-scores (subtract the
mean, divide by the standard deviation), so each contributes comparable
variance to Euclidean distance. The choice of scaling is itself a weighting
decision; standardising says "every column matters equally". If one column
should matter more, that's a deliberate choice, not a default.

## Choosing k: the Elbow Method
**Simple:** Plot how tight the clusters are for k = 2, 3, 4... More clusters are
always tighter, but at some point the gains shrink. Look for the bend in the
curve, where adding another cluster stops buying much.

**Deeper:** Inertia decreases monotonically with k, so its minimum is useless.
The elbow is the point of diminishing returns. On real data it's often a soft
curve, and different people will read it differently. The script estimates it
as the point furthest from the straight line joining the first and last values.

## Choosing k: the silhouette score
**Simple:** For each customer, ask: how close am I to my own cluster versus the
next-nearest one? +1 means clearly in the right group, 0 means on the border,
negative means probably in the wrong group. Average it across everyone.

**Deeper:** For point i, s(i) = (b - a) / max(a, b), where a is the mean
distance to points in its own cluster and b the mean distance to points in the
nearest other cluster. The mean silhouette rewards compact, separated clusters.
It favours convex, similar-sized clusters, as K-means does, so it can't detect
when K-means is the wrong tool.

## Centroids
**Simple:** The centroid is the "average customer" in a cluster. Compare it to
the overall average to see what makes that cluster different.

**Deeper:** Centroids are computed in scaled space and transformed back to
original units for reading. The z-score profile (centroid minus overall mean,
divided by standard deviation) shows distinctiveness on a common scale: about
+/-1 is very distinctive.

## What drove the split
**Simple:** For each column, how much of the difference between customers is
explained by which cluster they're in? A high percentage means that column
separates the clusters strongly.

**Deeper:** This is eta-squared: between-cluster sum of squares divided by
total sum of squares, per feature. It shows which features the partition
actually uses. In unscaled data, it exposes the dominant-feature problem.

## PCA plot
**Simple:** We have five columns, but a screen has two dimensions. PCA finds
the two directions where customers differ most and draws everyone on that
flat map. Close points are similar customers. Some information is lost, so
clusters that overlap on the map may be separate in reality.

**Deeper:** PCA projects standardised data onto the top principal components.
The axis labels show the share of variance each captures. If the two
components capture under ~60%, treat the picture as a rough sketch.

## Local minima (the "unlucky start")
**Simple:** Where the shops start matters. A bad start can leave two shops
fighting over one neighbourhood and another neighbourhood with none. The fix
is to try many starts and keep the best.

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
