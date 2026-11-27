# PR Response Doc — CineLog Watchlist Feature

## AI Usage
I used Claude to help understand the conventions of the collection_service feature and its tests. I also used Claude to debug my rebase and commit processes, because I ran into a few issues due to unfamiliarity with some of the process.

## Comment 1 — Rename
**What I did:** Renamed add_to_watchlist() to save_to_watchlist
**How I verified:** Performed a proejct-wide search for "save_to_watchlist()" to ensure the results were None

## Comment 2 — Deduplication
**What I did:** I added dedeuplication logic for add_to_watclist() using the convention from add_to_collection(). This convention is to define a boolean variable for whether a query search for the film returns a value or is None. If the variable is true, an exception is raised and the film is not added to the watchlist.
**How I verified:** I had Claude run a test and show the results.

## Comment 3 — Missing test
**What I did:** I created tests for watchlist_service.py following the conventions of test_collection.py. I modeled the tests using all three tests from test_collection.py, as both the watchlist_service and collection_service have similar functions that needed similar tests. These tests include: `test_add_to_watchlist_creates_entry`, `test_add_to_watchlist_duplicate_raises`, `test_add_to_watchlist_nonexistent_film_raises`, and `test_get_watchlist_returns_alpha_first`. The most different deviation I had to make was for testing the sorting order. The films stored collection are sorted by date added, while watchlist is sorted in alphabetical order.
**How I verified:** I ran the tests in the terminal and all four passed.

## Comment 4 — Default visibility
**My position:** If we're optimizing Cinelog for users who consider themselves film snobs, a public watchlist seems to be the best choice. 
**Reasoning:** Thinking of similar film logging services (ex Letterboxd), people often use the movies theyve watched or plan to watch as indicators of their interests and sometimes even of their personal values, beliefs and character traits. With Cinelog, showing the films that the user plans to watch publicly follows this formula.
**Tradeoff acknowledged:** However, some users may prefer more privacy for numerous reasons. They may have embarrasment for certain films they add to their watchlist, or may not want people to know that they haven't seen a certain film yet. They may also just not want to use Cinelog in the way other film logging services are used, and just for their own personal viewing purposes. Future updates could include an option for the user to toggle watchlist visibility.

## Comment 5 — Sort order
**My position:** There should be a toggle that allows the user to switch between sorting views.
**Reasoning:** Sorting by date added makes sense to remind a user of a film they were thinking of watching more recently, and allowing them to view what films they've had on their watchlist for a while but still have not watched. Sorting by alphabetical can aid in the user finding a specific title if they don't remember when they added it to their watchlist, but know where the title should show up alphabetically. Since both sorting options serve a purpose, the user should be able to toggle between the two. I do feel that it should default to date added sorting, before the user chooses to toggle.
**Engagement with reviewer's point:** Since more users seem to prefer date added sorting, that can be the default, but they should also have the option to toggle.


## Comment 6 — Rebase
**What conflicted:** There was a merge conflict due to models.py.
**How I resolved it:** It was resolved by using user id's for both foreign keys.
**How I verified no conflict remains:** The rebase worked the second time.

## PR Description
The watchlist feature allows users to add films to a watchlist. If a film is not found, or if the film is already in the user's watchlist, errors will be raised. The watchlist is sorted in alphabetical order as of now, but there is a possibility to default the sorting to the date the film was added and allowing the user to toggle between sorting options. The default visibility for the user's watchlist is public, and I think this should stay the default, but that the user should have the option to make it private. There were tests written in test_collection.py that I rewrote to test the watchlist feature in test_watchlist.py. It tests adding a film to the list, the deduplication feature, raising an error when the film doesn't exist, and the sorting order of the watchlist.

## Screenshot 

<img width="1518" height="320" alt="image" src="https://github.com/user-attachments/assets/6728bd41-e79b-467a-8716-89a1d614ad1c" />
