# PR Response Doc — CineLog Watchlist Feature

## AI Usage
<!-- Filled in at the end -->

## Comment 1 — Rename
**What I did:**
Renamed `save_to_watchlist()` → `add_to_watchlist()` in `services/watchlist_service.py` to match the project's `verb_to_noun` convention already established by `add_to_collection()` / `remove_from_collection()`. Updated the sole call site in `routes/watchlist/watchlist.py` (both the import and the invocation).

**How I verified:**
`grep -rn "save_to_watchlist" --include="*.py" .` returned zero results after the change. Full suite still passes (`pytest tests/ -v`).

## Comment 2 — Deduplication
**What I did:**
Added a `AlreadyInWatchlistError` exception and a duplicate check in `add_to_watchlist()`, mirroring the pattern in `add_to_collection()`: after the `FilmNotFoundError` check, query `WatchlistEntry` for `(user_id, film_id)` and raise if one exists — rather than relying on a DB-level `UniqueConstraint` alone.

**How I verified:**
Read `services/collection_service.py::add_to_collection` first — its dedup runs a `filter_by(...).first()` and raises `AlreadyInCollectionError` before hitting the DB integrity error. Mirrored that. Added a test in `tests/test_watchlist.py` for the duplicate case (see Comment 3 / stretch tests). `pytest tests/ -v` green.

## Comment 3 — Missing test
**What I did:**
Created `tests/test_watchlist.py` following the fixture and assertion style of `tests/test_collection.py` (same `app`, `sample_user`, `sample_film` fixtures). Wrote `test_add_to_watchlist_nonexistent_film_raises` as the direct equivalent of `test_add_to_collection_nonexistent_film_raises` — passes a UUID that isn't in the DB and asserts `FilmNotFoundError`.

**How I verified:**
`pytest tests/test_watchlist.py -v` — the new test passes; `pytest tests/ -v` — full suite green.

## Comment 4 — Default visibility
**My position:**
<!-- YOUR OWN reasoning — see draft in the section below and rewrite in your voice -->

**Reasoning:**

**Tradeoff acknowledged:**

## Comment 5 — Sort order
**My position:**
<!-- YOUR OWN reasoning — see draft below and rewrite -->

**Reasoning:**

**Engagement with reviewer's point:**

## Comment 6 — Rebase
**What conflicted:**
`models.py` — the main branch changed `Film.id` and `CollectionEntry.film_id` to `String(36)` UUIDs; my feature branch still had them as `Integer` and defined `WatchlistEntry.film_id` as `Integer`. Also `services/watchlist_service.py` and `routes/watchlist/watchlist.py` referenced integer IDs in docstrings/comments.

**How I resolved it:**
`git fetch origin && git rebase origin/main`. For each conflict I took main's UUID version of `Film.id` and `CollectionEntry.film_id`, and updated `WatchlistEntry.film_id` from `Integer` to `String(36)` to match. Updated docstrings/type hints in the watchlist service and route from `int` → `str` (UUID). No merge commits — the branch is linear.

**How I verified no conflict remains:**
`git status` clean, `git log --oneline --graph` shows no merge nodes, `pytest tests/ -v` still green after the rebase.

## PR Description
<!-- Written at the end -->
