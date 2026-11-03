"""Tests for the watchlist service."""

from datetime import datetime, timedelta, timezone

import pytest

from app import create_app, db
from models import Film, User, WatchlistEntry
from services.collection_service import FilmNotFoundError
from services.watchlist_service import add_to_watchlist, get_watchlist


@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """A user to use in tests."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id


def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """Adding a film_id that doesn't exist should raise FilmNotFoundError."""
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)


def test_get_watchlist_returns_newest_first(app, sample_user):
    """The most recently added film should appear first in the watchlist."""
    with app.app_context():
        earlier_film = Film(title="Alien", year=1979, genre="Horror")
        later_film = Film(title="Blade Runner", year=1982, genre="Sci-Fi")
        db.session.add_all([earlier_film, later_film])
        db.session.commit()

        earlier = datetime.now(timezone.utc) - timedelta(days=5)
        later = datetime.now(timezone.utc)
        db.session.add_all([
            WatchlistEntry(
                user_id=sample_user, film_id=earlier_film.id, date_added=earlier
            ),
            WatchlistEntry(
                user_id=sample_user, film_id=later_film.id, date_added=later
            ),
        ])
        db.session.commit()

        watchlist = get_watchlist(sample_user)

        assert [film["title"] for film in watchlist] == [
            "Blade Runner",
            "Alien",
        ]
