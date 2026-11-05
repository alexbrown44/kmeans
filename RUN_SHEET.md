# Run sheet: K-means demo, Monday 9 November 2026

**Slot:** 10–15 minutes. **Where:** Claude chat, with the kmeans-teacher skill.
**Flow:** data → scaling → choosing k → segments → replay → campaigns → noise trap.

Type each prompt exactly as written, one at a time. Wait for Claude to finish before
you talk over the result. Expected numbers come from the seeded scripts and should
match every time; if one doesn't, see "If it goes wrong" at the bottom.

---

## Before class (10 minutes earlier)

- [ ] Latest `kmeans-teacher.zip` uploaded in **Customize > Skills**, toggle **on**
- [ ] **Settings > Capabilities**: code execution on
- [ ] A **new chat** open, browser zoomed so the back row can read it (Ctrl and +)
- [ ] Second tab open on the demo: <https://claude.ai/artifact/KH7dmKcYzkBTdKz1MRDdzk>
- [ ] README link ready to paste in the class chat: <https://github.com/alexbrown44/kmeans>

---

## 1. The data · 1½ min

> I'm running a classroom demo. Use the synthetic e-commerce customer data, in classroom demo mode. Start with the data, then stop.

**If two question cards appear** (which data, which mode), click **Synthetic e-commerce**, then **Classroom demo**.

**Expect:** 800 synthetic customers. It recommends clustering on Age, AnnualIncome,
SpendingScore, TimeOnSite and NumberOfVisits, and leaves out CustomerID, Gender and
PreferredCategory.

**Say:** "Five kinds of customer are hidden in this data. K-means isn't told what they
are. Let's see if it finds them." *Don't name them yet.*

## 2. Why scaling matters · 2 min

> Show me why scaling matters.

**Expect:** the height-in-millimetres analogy, then a small table of five groups.
Average income climbs from about **$41k to $140k**, while spending and visits barely
change. **No scores yet**: the silhouette comes in step 3.

**Say:** "It hasn't found kinds of customer. It's sorted people by income, because
income has the biggest numbers. So first we put every column in the same units,
and every column gets a fair say."

## 3. Choosing k · 3 min (the key moment)

> How many segments should we use?

**Expect:** it explains each chart before quoting it: the elbow (shop-staff analogy)
bends at **5**; the silhouette (party analogy, 0-to-1 scale) peaks at **4** (0.51 vs
0.47). It may add that the income-band groups from step 2 score only about 0.04. At
k=4, low spenders who visit rarely form one big group. At k=5 they split by income:
people who **can't** spend (about $60k) and people who **won't** (about $124k).
**It should stop and ask you.**

**Ask the room:** "Do we want the higher score, or the split marketing can use?"
Take a show of hands, then:

> Use k=5. I want to separate customers who can't spend from customers who won't.

**Say:** "The algorithm didn't choose k. We did, from the business question."

## 4. The segments · 2½ min

If Claude hasn't shown them yet:

> Show me the segments and name them.

**Expect:** silhouette **0.47** ("real groups, some overlap"). Five segments:

| Segment | Size | Stands out for |
|---|---|---|
| Low-budget occasionals | 207 (26%) | ~$60k, spend 23, 3 visits/month |
| Engaged browsers | 192 (24%) | 23 min a visit, 16 visits, but spend only 29 |
| High-value loyalists | 144 (18%) | ~$116k, spend 82, 14 visits |
| Young enthusiasts | 144 (18%) | age 24, ~$38k, yet spend 75 |
| Affluent but disengaged | 113 (14%) | ~$124k, age 54, spend 18, 2 visits |

Names may be worded slightly differently. Sizes should match exactly.

**Say:** "Those are the five segments we hid. K-means found them without being told."

## 5. Watch it run · 1½ min

**Switch to the demo tab.** Don't build the explorer live; the published one is the same
data and won't keep the room waiting.

1. Click **Watch it run**, then **Step** a few times: dots join the nearest centroid,
   then the centroids slide to the middle. Click **Play** to finish: **done in 6 rounds**.
2. Tick **Unlucky start**, then **Play**: stuck after 14 rounds, **85% worse**.

**Say:** "Same data, bad starting points, worse answer. That's why real K-means
runs 10 starts and keeps the best."

## 6. Campaigns · 1½ min

> Give me one campaign per segment, then a reality check.

**Expect:** five different campaigns. The reality check flags **Affluent but disengaged**
as the smallest segment (14%), worth its own campaign only if a test shows it responds
differently.

**Say:** "Segments only pay off if they respond differently. Test before you spend."

## 7. The noise trap · 2 min

> How do we know these segments are real? Show me the noise trap.

**Expect:** on pure random data, K-means still returns five neat groups you could name.
But the silhouette is about **0.15** and stays flat (0.14–0.18) for every k.

**Say:** "K-means always gives you an answer. The silhouette, and your judgment, tell
you whether to trust it."

## Close · 30 sec

**Say:** "Real data is messier. In the repo there's real wholesale data: it scores 0.29,
and still separates restaurants from retailers without being told. That's your homework.
The link's in the chat." *Paste the README link.*

**Total: about 14½ minutes.** Running long? Cut step 6 to one campaign, the opportunity
segment (Affluent but disengaged).

---

## If it goes wrong

| What happens | What to type or do |
|---|---|
| Claude runs ahead through several steps | "Stop there. One step at a time, please." Carry on from wherever it reached. |
| It picks k itself | "Go back to choosing k. Show me both scores and let me choose." |
| It quotes scores or jargon in step 2 | "Say that again without any scores, just show me the groups' average income and spending." |
| A script errors or hangs over a minute | Say "live demos…", switch to the demo tab, and walk through it there. |
| Numbers don't match this sheet | Keep going; the story still works. Tell me after class. |
| The skill doesn't trigger at all | Check the toggle in Customize > Skills, start a new chat, retype prompt 1. |
