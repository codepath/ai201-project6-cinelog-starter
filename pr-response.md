# PR Response Doc — CineLog Watchlist Feature

## AI Usage
<!-- Fill in at the end — how you used AI tools during this project -->

## Comment 1 — Rename
**What I did:** Renamed `save_to_watchlist()` to `add_to_watchlist()` in `services/watchlist_service.py` so it matches the verb_to_noun convention the rest of the codebase uses (`add_to_collection()`, `remove_from_collection()`, etc). Then I updated the one call site in `routes/watchlist/watchlist.py` — both the import line at the top and the actual call inside `add_film()`. I almost missed the import since I was only looking for the function call at first.
**How I verified:** I did a project-wide search for `save_to_watchlist` across all the `.py` files (and the `.md` files too, in case the README or CONTRIBUTING mentioned it). Before the fix it showed up in 2 spots, both in `routes/watchlist/watchlist.py` (line 8 import, line 32 call). After the fix the search comes back with nothing. Then I ran `pytest tests/ -v` and all 4 existing tests still passed.

## Comment 2 — Deduplication
**What I did:** I used `add_to_collection()` in `services/collection_service.py` as the pattern since it already handles this exact problem. After it confirms the film exists, it runs `CollectionEntry.query.filter_by(user_id=user_id, film_id=film_id).first()` to look for an existing row with the same user AND the same film. If it finds one, it doesn't insert anything and instead raises `AlreadyInCollectionError` with a message saying the film is already in the user's collection. So a duplicate never makes it to `db.session.add()`.

I did the same thing in `add_to_watchlist()`: added an `AlreadyInWatchlistError` exception class (same style as `AlreadyInCollectionError`), and after the film-exists check I query `WatchlistEntry` filtered by `user_id` and `film_id`. If there's already a match it raises `AlreadyInWatchlistError` before anything gets added or committed. I kept the order the same as `add_to_collection()` too (check film exists first, then check for duplicate) so a bad film id still gives `FilmNotFoundError`. I also updated the docstring's Raises section.
**How I verified:** I ran a quick script against an in-memory DB: made a user and a film, called `add_to_watchlist()` once, then called it again with the same ids. The second call raised `AlreadyInWatchlistError` and the count of `WatchlistEntry` rows for that user/film stayed at 1. Then I ran `pytest tests/ -v` and all 4 tests still passed. (One thing to note — the route doesn't catch `AlreadyInWatchlistError` yet, so a duplicate POST would currently return a 500 instead of something like a 409. I left the route alone since that wasn't part of this comment, but I can add it if you want.)

## Comment 3 — Missing test
**What I did:** Created `tests/test_watchlist.py` and added `test_add_to_watchlist_nonexistent_film_raises`. I modeled it on `test_add_to_collection_nonexistent_film_raises` in `tests/test_collection.py`. I copied over the same `app` fixture (in-memory SQLite, `create_all` / `drop_all` around each test) and the `sample_user` fixture, and kept the same structure: open an app context, make a fake film id, then use `pytest.raises(FilmNotFoundError)` around the `add_to_watchlist()` call. I didn't bring over `sample_film` since this test doesn't need a real film. The one thing I changed is the fake id: the collection test uses a UUID string, but `Film.id` is an Integer column and the `add_to_watchlist()` docstring says `film_id` is an int, so I used `99999` to match what the watchlist actually gets passed.
**How I verified:** Ran `pytest tests/test_watchlist.py -v` and the new test passed. Then ran the full suite with `pytest tests/ -v` and all 5 tests passed (4 collection + 1 watchlist).

## Comment 4 — Default visibility
**My position:**
**Reasoning:**
**Tradeoff acknowledged:**

## Comment 5 — Sort order
**My position:**
**Reasoning:**
**Engagement with reviewer's point:**

## Comment 6 — Rebase
**What conflicted:**
**How I resolved it:**
**How I verified no conflict remains:**

## PR Description
<!-- Written at the end — feature overview, design decisions, manual testing steps -->