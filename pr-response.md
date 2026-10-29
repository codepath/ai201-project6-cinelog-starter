# PR Response Doc — CineLog Watchlist Feature

## AI Usage
**Codebase orientation and matching patterns:** Before changing the watchlist code, I used Claude Code (an AI coding assistant) to read `services/collection_service.py`, `routes/collection.py`, and `tests/test_collection.py`, so my changes would follow the conventions already in the codebase instead of new ones. That shaped three of my changes. I renamed `save_to_watchlist()` to `add_to_watchlist()` to match the `verb_to_noun` naming of `add_to_collection()`. I modeled the duplicate check on the collection's version: look up an existing `user_id`/`film_id` pair, raise a dedicated exception (`AlreadyOnWatchlistError`, like `AlreadyInCollectionError`), and map it to 409 in the route. I wrote `test_add_to_watchlist_nonexistent_film_raises()` with the same fixtures, fake UUID, and `pytest.raises(FilmNotFoundError)` assertion as the collection test. I checked each change against the collection code myself and ran `pytest tests/ -v` to confirm the suite passed.

**Comments 4 and 5:** TODO: describe what you asked the AI about the visibility default and sort order, what it suggested, and how your final argument differs from or builds on that.

## Comment 1 — Rename
**What I did:** Renamed `save_to_watchlist()` to `add_to_watchlist()` in the service and updated the route import and call site to match the project's `verb_to_noun` convention (the existing collection feature uses `add_to_collection()`). Commit: `refactor: rename watchlist service function` (`ee9040c`).
**How I verified:** Searched the entire project for `save_to_watchlist()`. The search found its definition in `services/watchlist_service.py` and its import/call in `routes/watchlist/watchlist.py`; both were updated. A follow-up search found no remaining code references to the old name.

## Comment 2 — Deduplication
**What I did:** Followed `add_to_collection()` in `services/collection_service.py`: its duplicate check searches for an existing entry matching both `user_id` and `film_id`, then raises `AlreadyInCollectionError` when found. `add_to_watchlist()` now checks for the same user/film pair and raises `AlreadyOnWatchlistError` for a duplicate; the route returns HTTP 409 Conflict. Before this change, adding the same film twice silently created a second watchlist row. Commit: `fix: prevent duplicate watchlist entries` (`5862d7f`).
**How I verified:** Added `test_add_to_watchlist_duplicate_raises()`, which adds the same film twice, asserts the second call raises `AlreadyOnWatchlistError`, and checks that only one row remains. At that point, `pytest tests/test_watchlist.py tests/test_collection.py` passed (5 tests) and the full `pytest tests/ -v` suite passed (6 tests; the seventh, the sort-order test, came later with Comment 5). I also confirmed manually that a second `POST` of the same film returns 409.

## Comment 3 — Missing test
**What I did:** Added `test_add_to_watchlist_nonexistent_film_raises()`, which calls `add_to_watchlist()` with a made-up film UUID and asserts it raises `FilmNotFoundError`. I modeled it on `test_add_to_collection_nonexistent_film_raises()` in `tests/test_collection.py`: same isolated in-memory app and sample-user fixtures, fake UUID, and `pytest.raises` assertion.
Testing this case end to end also exposed a related bug: the watchlist route imported `FilmNotFoundError` but never caught it, so `POST /watchlist/<user_id>/add` with an unknown film returned **500 Internal Server Error**. I added the same `except FilmNotFoundError` → 404 handler that `routes/collection.py` uses. Commit: `fix: return 404 when adding a nonexistent film to watchlist` (`cb5b596`).
**How I verified:** Ran `pytest tests/test_watchlist.py -v`, and the nonexistent-film test passed. Then I ran the app against a seeded database and posted an all-zeros UUID to `/watchlist/<user_id>/add`: it returned 500 before the route fix and 404 with a "No film found" error after it.

## Comment 4 — Default visibility
**My position:** Keep `public=True` as the default (`WatchlistEntry.public = db.Column(db.Boolean, default=True)` in `models.py`), but treat it as a deliberate product choice rather than an incidental model default. No code change was needed. I documented the decision and its tradeoff here and in the PR description.
**Reasoning:** This community film-tracking app should make it easy for users to share what they want to watch and discover films through other users' lists. A public default optimizes for users who add films to participate in that shared discovery, without making them configure visibility on every entry. Users should still be able to make an entry private, but the current API has no way to do that: `POST /watchlist/<user_id>/add` doesn't accept a `public` field, and there's no update endpoint. I've noted this as a follow-up in the PR description rather than expanding this PR's scope.
**Tradeoff acknowledged:** A private-by-default policy would better protect users who consider their interests personal, and avoids exposing a list before the user makes an explicit choice. The cost is less immediate sharing and discoverability, plus added friction for users who intend to participate publicly. Because this feature is community-oriented, I favor public-by-default here, while recognizing that a privacy-first product should reverse that choice.

## Comment 5 — Sort order
**My position:** Use newest-added-first ordering, matching the reviewer's preference; `get_watchlist()` now orders entries by `date_added` descending.
**Reasoning:** Recently saved films are likely to be the most immediately relevant. This also keeps watchlist behavior consistent with `get_collection()`, which already returns entries newest first.
**Engagement with reviewer's point:** The reviewer noted that users usually want to see what they added recently. I agree that this is a better default than alphabetical order for a watchlist centered on films saved for later. Alphabetical ordering may still help users browse a large list, but it can be added later as an optional sort rather than overriding the recent-first default. Commit: `fix: sort watchlist by date added` (`1cd2091`).
**How I verified:** Added `test_get_watchlist_returns_newest_first()`. It adds "Alien" and then "Blade Runner" and asserts that "Blade Runner" comes first. Because those titles are in alphabetical order, the test would fail under alphabetical sorting, so it really checks the `date_added` order.

## Comment 6 — Rebase
**Background:** While this branch was open, `main` received `refactor: migrate film IDs from integer to UUID` (`57ec3f9`), which changed `Film.id` from an auto-increment integer to a UUID string. Any watchlist code that still treated film IDs as integers would break against the new schema.
**What conflicted:** During the earlier rebase onto the UUID refactor, `WatchlistEntry.film_id` conflicted: the feature side declared `Integer`, while main declared `String(36)` to match UUID-based `Film.id`.
**How I resolved it:** Kept main's UUID-compatible `String(36)` foreign key. For this review request, fetched `origin` and ran `git rebase origin/main`; it completed without replay conflicts because `origin/main` was already an ancestor of the feature branch. Then committed the remaining stale integer references separately: the service documents `film_id` as a UUID string and the route documents a UUID request value. Commit: `fix: update WatchlistEntry film_id to UUID after main branch refactor` (`24bd4dd`).
**How I verified no conflict remains:** `Film.id`, `CollectionEntry.film_id`, and `WatchlistEntry.film_id` are UUID-compatible `String(36)` columns; the service and route no longer document integer film IDs. `git log --merges origin/main..HEAD` returned no merge commits. The full `pytest tests/ -v` suite passed after restoring the sort-order work (7 tests).

![git log after rebasing: feature/watchlist commits sit directly on top of main's UUID refactor (57ec3f9), with no merge commits](image.png)

![pytest tests/ -v: all 7 collection and watchlist tests passing](screenshot.png)

**Later cleanup:** After the screenshot above was taken, I found that a later commit had accidentally added the whole `.venv` folder and `__pycache__` files (about 2,900 files), because the repo had no `.gitignore`. I replaced that commit with three clean ones (`.gitignore`, the 404 route fix from Comment 3, and these docs) and force-pushed my fork's branch. The branch is still linear and based directly on `main`.

## PR Description

### What this does
Adds a watchlist so users can save films they want to watch later, separate from their collection of films they've already logged. `POST /watchlist/<user_id>/add` saves a film by UUID, and `GET /watchlist/<user_id>` returns the saved films with each entry's `date_added` and `public` flag. Adding a film that doesn't exist returns 404, and adding a film that's already on the user's watchlist returns 409, the same way the collection endpoints behave.

### Design decisions
1. **Visibility default: public.** New watchlist entries are created with `public=True`. CineLog is a community app, and public watchlists let people find films through each other's lists without changing a setting on every entry. The tradeoff is that someone who thinks of their watchlist as personal is sharing it before making a choice. This PR doesn't add an endpoint for making an entry private; that would be a follow-up. A privacy-first product would make the opposite choice.
2. **Sort order: newest added first.** `get_watchlist()` orders by `date_added` descending. Films saved recently are usually the ones the user cares about right now, and this matches `get_collection()`, which also returns newest first. Alphabetical order would help when browsing a long list, so it could be added later as an optional sort, not as the default.

### How to test manually
1. Install dependencies and seed a database:
   ```bash
   pip install -r requirements.txt
   python seed.py
   ```
   Note the `user_id` that `seed.py` prints for the `demo` user.
2. Start the app: `python app.py` (serves on `http://localhost:5000`).
3. List films and copy two film `id` values:
   ```bash
   curl http://localhost:5000/films/
   ```
4. Add the first film:
   ```bash
   curl -X POST http://localhost:5000/watchlist/<user_id>/add \
     -H "Content-Type: application/json" -d '{"film_id": "<film_id_1>"}'
   ```
   Expect **201** and an entry with `"public": true`.
5. Wait a second, then repeat step 4 with `<film_id_2>`. Expect **201**.
6. Repeat step 4 with `<film_id_1>` again. Expect **409** with an "already on this user's watchlist" error.
7. Repeat step 4 with `{"film_id": "00000000-0000-0000-0000-000000000000"}`. Expect **404** with a "No film found" error.
8. Repeat step 4 with an empty body `{}`. Expect **400** with "film_id is required".
9. Get the watchlist:
   ```bash
   curl http://localhost:5000/watchlist/<user_id>
   ```
   Expect two films, each with `date_added` and `"public": true`, and film 2 listed **before** film 1 (newest first).
10. Run the automated tests: `pytest tests/ -v` (7 tests should pass).
