# PR Response Doc — CineLog Watchlist Feature

## AI Usage
<!-- Fill in at the end — how you used AI tools during this project -->

## Comment 1 — Rename
**What I did:** Renamed add_to_watchlist() to save_to_watchlist
**How I verified:** Performed a proejct-wide search for "save_to_watchlist()" to ensure the results were None

## Comment 2 — Deduplication
**What I did:** I added dedeuplication logic for add_to_watclist() using the convention from add_to_collection(). This convention is to define a boolean variable for whether a query search for the film returns a value or is None. If the variable is true, an exception is raised and the film is not added to the watchlist.
**How I verified:** I had Claude run a test and show the results.

## Comment 3 — Missing test
**What I did:**
**How I verified:**

## Comment 4 — Default visibility
**My position:**
**Reasoning:**
**Tradeoff acknowledged:**

## Comment 5 — Sort order
**My position:**
**Reasoning:**
**Engagement with reviewer's point:**

## Comment 6 — Rebase
**What conflicted:** There was a merge conflict due to models.py.
**How I resolved it:** It was resolved by using user id's for both foreign keys.
**How I verified no conflict remains:** The rebase worked the second time.

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->