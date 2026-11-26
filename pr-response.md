# PR Response Doc — CineLog Watchlist Feature

## AI Usage
I used Claude Code (inside VS Code) pretty heavily on this project, so here's what it did and what I did:

- **Understanding the pattern:** It explained what the duplicate check in `add_to_collection()` does: it queries `CollectionEntry` by `user_id` + `film_id`, and if a row already exists it raises `AlreadyInCollectionError` instead of inserting. That's what I used to describe the pattern in Comment 2.
- **Comments 4 and 5:** I picked the positions (keep `public=True`, switch to date added) and used AI to help write them up and act as a devil's advocate. The most useful thing it caught was in Comment 4. My argument assumed users could make entries private, but there's no endpoint to change `public`, and `get_watchlist()` doesn't filter on it, so the flag doesn't actually do anything yet. I added that to the tradeoff section along with the follow-up plan. For Comment 5, it pushed on the "long lists are hard to scan" point, which is where the `?sort=title` idea came from.
- **Rebase:** When `git fetch` failed, it found the stale lock/duplicate ref files in `.git` and removed them after checking that no git process was running. It also did the rebase. I decided how to resolve the `models.py` conflict (keep the UUID type, keep the index).

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
**My position:** Keep `public=True` as the default for watchlist entries.

**Reasoning:** The README describes CineLog as a community film tracking app, so the social side is a big part of the point. A watchlist is one of the most useful things to share on a platform like this: friends can see what you're planning to watch, you can find movies through people you follow, and it makes it easy to plan watching something together. The user behavior I'm optimizing for is discovery. If watchlists start out private, most of them will just stay private, because most people never go into settings and change a default. That would leave the community side of the app pretty empty.

The other part of my reasoning is about what's actually being shared. A watchlist is just film titles someone *wants* to watch. There aren't ratings or reviews attached, so it's lower stakes than something like a collection with ratings. Also, `public` is stored on each `WatchlistEntry`, not on the whole list, so a user could hide one specific film without making their whole watchlist private. That's more flexible than an all-or-nothing setting.

**Tradeoff acknowledged:** The big downside is privacy. Since defaults basically end up being the decision for most people, public-by-default means a lot of users will be sharing their watchlist without really deciding to. Some film choices can say personal things about someone (like a film about a health issue, their sexuality, religion, etc.), and that person might not realize it's visible. Private-by-default would avoid that, and it's honestly the safer choice.

When I was stress-testing this, I also realized my argument depends on users being *able* to change visibility, and right now they can't. There's no endpoint to toggle `public`, and `get_watchlist()` returns every entry whether it's public or not, so the flag isn't actually enforced anywhere yet. I don't think public-by-default is OK to ship until both of those exist. I'd like to do them as a follow-up PR: a way to set `public` (either in the add request body or a separate update endpoint), and filtering out private entries when someone views another user's watchlist. If you'd rather not merge this until those are in, I understand. In that case I'd switch the default to `False` for now and change it back once users can actually control it.

## Comment 5 — Sort order
**My position:** I switched to date added (newest first).

**Reasoning:** I originally used alphabetical because I was picturing someone scanning their list for a specific title. But after thinking about how a watchlist actually gets used, I think date added makes more sense. A watchlist is more like a queue than a catalog. The stuff you added most recently is usually what you're most interested in right now, like a movie a friend just recommended or a trailer you just saw. It also matches `get_collection()`, which already sorts by `date_added` descending, so both list endpoints in the API now behave the same way. That's one less thing someone has to remember about the API.

Code changes: in `get_watchlist()` I changed `.order_by(Film.title.asc())` to `.order_by(WatchlistEntry.date_added.desc())` and updated the docstring (commit `fix: sort watchlist by date added instead of alphabetically`). Then I added `test_get_watchlist_returns_newest_first` to `tests/test_watchlist.py`, modeled on `test_get_collection_returns_newest_first`. It adds "Alien" 5 days ago and "Blade Runner" now and checks that Blade Runner comes first. Alphabetical order would put Alien first, so the test would actually catch it if the sorting went back to alphabetical (commit `test: add test for get_watchlist sort order`). All tests pass.

**Engagement with reviewer's point:** I agree with "most users want to see what they added recently," and I think it's even more true for watchlists than collections, because a watchlist is about what you want to do *next*. The one thing I'd push back on a little is that my alphabetical concern doesn't totally go away. Once someone's watchlist gets long (like 100+ films), finding a specific title by scrolling through date order is annoying, and older films can sink to the bottom and get forgotten. I don't think that's a reason to change the default, though. It's more of a search/sort problem. If it ends up being an issue, I think the cleanest fix would be an optional `?sort=title` query param on `GET /watchlist/<user_id>`, with date added staying as the default. I left that out of this PR to keep it focused, but I'm happy to add it if you think it's worth it.

## Comment 6 — Rebase
**What conflicted:** I ran `git fetch origin` and then `git rebase origin/main`. It stopped on my first watchlist commit (the one that added the `WatchlistEntry` model) with a conflict in `models.py` on the `film_id` column:
- `main` (after the UUID refactor): `film_id = db.Column(db.String(36), db.ForeignKey("film.id"), nullable=False)`
- my branch: `film_id = db.Column(db.Integer, db.ForeignKey("film.id"), nullable=False, index=True)`

Side note: the fetch failed the first time with "did not send all necessary objects". It turned out there were some leftover files in `.git` (duplicate `HEAD 2` refs and old empty `.lock` files from a git process that crashed on Nov 12), and they were blocking `origin/main` from being created. I checked that no git processes were running, deleted the stale files, and then the fetch and rebase worked.

**How I resolved it:** I kept main's `db.String(36)` type, since film IDs are UUIDs now and `Film.id` is a `String(36)` column, so the foreign key has to match. I also kept my `index=True`, because the watchlist looks up rows by `film_id` (like in the new duplicate check), so the index is still useful. Final line: `film_id = db.Column(db.String(36), db.ForeignKey("film.id"), nullable=False, index=True)`. Then `git add models.py` and `git rebase --continue`, and the rest of my commits replayed without conflicts.

The rebase only fixed the model, so after it finished I searched the watchlist files for anything else still assuming integer IDs and found three:
- `services/watchlist_service.py`: docstring said `film_id (int): ID of the film. (Note: integer — pre-refactor)` → changed to `film_id (str): UUID of the film.`
- `routes/watchlist/watchlist.py`: endpoint docstring said `Body: { "film_id": <int> }` → changed to `<uuid>`
- `tests/test_watchlist.py`: the nonexistent-film test used `fake_film_id = 99999` → changed to `"00000000-0000-0000-0000-000000000000"`, which is the same fake UUID `test_collection.py` uses

I committed those separately as `fix: update WatchlistEntry film_id to UUID after main branch refactor`.

**How I verified no conflict remains:**
- Searched all `.py` files for `<<<<<<<` / `>>>>>>>` conflict markers. None left.
- Searched the watchlist service, route, and tests for `int` / `integer` / `pre-refactor`. No integer-ID references left.
- `git log --merges --oneline origin/main..HEAD` returns nothing, so there are no merge commits in my branch.
- `git log --oneline --graph` shows a straight line, with my commits sitting on top of `57ec3f9 refactor: migrate film IDs from integer to UUID`.
- Ran `pytest tests/ -v` and all 6 tests pass (4 collection + 2 watchlist), now running against the UUID version of the models.

## PR Description
### What this does
This adds a watchlist to CineLog. A watchlist is a list of films a user wants to watch later, separate from their collection of films they've already watched. Users can add a film to their watchlist with `POST /watchlist/<user_id>/add` and view it with `GET /watchlist/<user_id>`. Adding the same film twice is blocked, and adding a film that doesn't exist raises `FilmNotFoundError`, the same way the collection feature works.

### Design decisions
- **Visibility defaults to public (`public=True`).** CineLog is a community app, and watchlists are most useful when friends can see them (discovering films, planning to watch something together). Most users never change defaults, so private-by-default would mean almost nobody's watchlist is visible. The tradeoff is privacy: someone might not realize their list is visible, and film choices can reveal personal things. Right now there's no way for a user to change `public`, and `get_watchlist()` doesn't filter private entries yet. I'm planning to add both in a follow-up PR, and if that needs to happen before this merges, I'll switch the default to `False` until then. (Full reasoning in Comment 4.)
- **Watchlist is sorted by date added, newest first.** A watchlist works more like a queue than a catalog, since what you added most recently is usually what you're most interested in. This also matches how `get_collection()` already sorts. For long lists where finding a title by name matters, a `?sort=title` option could be added later. (Full reasoning in Comment 5.)
- **Follows existing patterns:** `add_to_watchlist()` uses the `verb_to_noun` naming convention, and its duplicate check works the same way as `add_to_collection()`. Film IDs are UUIDs to match main's refactor.

### How to test manually
1. Check out the branch and install dependencies:
   ```bash
   git checkout feature/watchlist
   pip install -r requirements.txt
   ```
2. Start from a fresh database. If you have an old `instance/cinelog.db` from before the UUID refactor, delete it first, because `seed.py` skips seeding if data already exists.
   ```bash
   rm -f instance/cinelog.db
   python seed.py
   ```
   Copy the `user_id` it prints for the demo user.
3. Start the app: `python app.py` (runs on `http://localhost:5000`).
4. Get some film IDs: `curl http://localhost:5000/films/` and copy two of the `id` values (they're UUIDs).
5. Add the first film to the watchlist:
   ```bash
   curl -X POST http://localhost:5000/watchlist/<user_id>/add \
     -H "Content-Type: application/json" \
     -d '{"film_id": "<film_id_1>"}'
   ```
   You should get a `201` with the new entry, and it should have `"public": true`.
6. Wait a second, then add the second film the same way using `<film_id_2>`.
7. View the watchlist: `curl http://localhost:5000/watchlist/<user_id>`. Both films should be there, and the second film you added should be **first** (newest first), whatever the titles are alphabetically.
8. Try adding the first film again. It should **not** create a second entry. Run step 7 again and there should still be only 2 films.
9. Try adding with an empty body (`-d '{}'`). It should return `400` with `"film_id is required"`.
10. Run the tests: `pytest tests/ -v`. All 6 should pass.

**Known limitation:** the route doesn't catch `AlreadyInWatchlistError` or `FilmNotFoundError` yet, so steps 8 and a bad film ID currently return a `500` instead of a cleaner `409`/`404`. No duplicate or bad data gets saved, though. I'd like to fix the status codes in the follow-up PR along with the visibility endpoint.