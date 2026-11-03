"""
services/watchlist_service.py — CineLog (feature/watchlist branch)

Business logic for the watchlist feature.
"""

from app import db
from models import Film, WatchlistEntry
from services.collection_service import FilmNotFoundError


<<<<<<< HEAD
class AlreadyOnWatchlistError(Exception):
    """Raised when a film is already on the user's watchlist."""


def add_to_watchlist(user_id, film_id):
    """
    Add a film to a user's watchlist.

    Args:
        user_id (str): UUID of the user.
        film_id (str): UUID of the film.
=======
def save_to_watchlist(user_id, film_id):
    """
    Save a film to a user's watchlist.

    Args:
        user_id (str): UUID of the user.
        film_id (int): ID of the film. (Note: integer — pre-refactor)
>>>>>>> af28e3c17551c9214411d8ff0f9972fabbae4029

    Returns:
        WatchlistEntry: The newly created entry.

    Raises:
        FilmNotFoundError: If film_id does not exist.
<<<<<<< HEAD
        AlreadyOnWatchlistError: If the film is already on the user's watchlist.
=======
>>>>>>> af28e3c17551c9214411d8ff0f9972fabbae4029
    """
    film = db.session.get(Film, film_id)
    if film is None:
        raise FilmNotFoundError(f"No film found with id '{film_id}'")

<<<<<<< HEAD
    existing = WatchlistEntry.query.filter_by(
        user_id=user_id, film_id=film_id
    ).first()
    if existing:
        raise AlreadyOnWatchlistError(
            f"Film '{film_id}' is already on this user's watchlist"
        )

=======
>>>>>>> af28e3c17551c9214411d8ff0f9972fabbae4029
    entry = WatchlistEntry(user_id=user_id, film_id=film_id)
    db.session.add(entry)
    db.session.commit()
    return entry


def get_watchlist(user_id):
    """
    Return all films on a user's watchlist.

    Args:
        user_id (str): UUID of the user.

    Returns:
        list[dict]: List of film dicts with watchlist metadata attached.
    """
    entries = (
        WatchlistEntry.query
        .filter_by(user_id=user_id)
        .join(Film)
<<<<<<< HEAD
        .order_by(WatchlistEntry.date_added.desc())
=======
        .order_by(Film.title.asc())
>>>>>>> af28e3c17551c9214411d8ff0f9972fabbae4029
        .all()
    )

    result = []
    for entry in entries:
        film_dict = entry.film.to_dict()
        film_dict["date_added"] = entry.date_added.isoformat()
        film_dict["public"] = entry.public
        result.append(film_dict)

    return result
