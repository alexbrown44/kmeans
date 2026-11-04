# K-means Teacher: a Claude skill

Learn K-means clustering by doing it. Claude segments a set of customers step by step, explains
each step in plain English, and builds an interactive explorer you can play with.

## ⬇️ [Download the skill (kmeans-teacher.zip)](https://github.com/alexbrown44/kmeans/raw/main/kmeans-teacher.zip)

**Just want to look?** Try the demo in your browser, no install needed:
**[Open the K-means explorer](DEMO-LINK-HERE)**

---

## Install it in 3 steps (about 2 minutes)

You need a Claude account on any plan, including Free. Use Claude on the web
([claude.ai](https://claude.ai)) or the Claude desktop app.

### 1. Download the zip
Click the **Download** link above. **Don't unzip it.** Claude wants the zip file itself.

> **On a Mac with Safari?** Safari sometimes unzips downloads automatically. If you see a folder
> called `kmeans-teacher` instead of a `.zip` file, right-click the folder and choose
> **Compress "kmeans-teacher"** to turn it back into a zip.

### 2. Turn on code execution
The skill runs real analysis, so Claude needs permission to run code.

1. In Claude, open **Settings**, then **Capabilities**.
2. Turn on **Code execution and file creation** (in some versions it's called **Create and edit files**).

### 3. Upload the skill
1. Go to **Customize**, then **Skills**.
2. Click **+**, then **+ Create skill**.
3. Choose **Upload a skill** and pick `kmeans-teacher.zip`.
4. Check that the **kmeans-teacher** toggle is **on**.

That's it.

## Try it

Start a new chat and type:

> Teach me K-means clustering using the sample customer data.

Claude will take it from there. You can also upload your own CSV or Excel file and say
*"Segment these customers with K-means."*

## If something goes wrong

| Problem | Fix |
|---|---|
| Upload fails | Make sure you're uploading the **.zip** file, not a folder, and that you haven't renamed it or re-zipped it with a different folder name. |
| No "Skills" or "Upload a skill" option | On a Team or Enterprise plan, your admin may need to turn on skills and code execution. |
| Claude answers but doesn't run any analysis | Check that code execution is on (step 2) and the skill's toggle is on (step 3). Then start a **new** chat. |

**Getting a newer version:** in **Customize > Skills**, turn the old skill off, click **...** next to it,
choose **Delete**, then upload the new zip.

## What's inside

- `kmeans-teacher/SKILL.md` contains the teaching steps Claude follows.
- `kmeans-teacher/scripts/` holds the analysis: sample data, clustering and the explorer page.
  The scripts are seeded, so the same data always gives the same answer.
- `kmeans-teacher/references/` has plain-English explanations at two levels.
- `kmeans-teacher/data/wholesale_customers.csv` is real data to try afterwards (see below).

**Homework: real data.** Once you've done the demo, ask Claude:
*"Does this work on real data? Try the wholesale customers file."*

The real dataset is [Wholesale customers](https://archive.ics.uci.edu/dataset/292/wholesale+customers)
by Margarida Cardoso (2013), UCI Machine Learning Repository, [doi:10.24432/C5030X](https://doi.org/10.24432/C5030X),
used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Columns were relabelled for
readability; see `kmeans-teacher/data/README.md`.
