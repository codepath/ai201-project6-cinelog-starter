"""
seed.py — CineLog

Populate the local SQLite database with a demo user and a few films.
Run once after installing dependencies: python seed.py
"""

from app import create_app, db
from models import User, Film

FILMS = [
    ("Paddington 2", 2017, "Paul King", "Comedy"),
    ("Alien", 1979, "Ridley Scott", "Horror"),
    ("Blade Runner", 1982, "Ridley Scott", "Sci-Fi"),
    ("Spirited Away", 2001, "Hayao Miyazaki", "Animation"),
    ("The Godfather", 1972, "Francis Ford Coppola", "Crime"),
]


def seed():
    app = create_app()
    with app.app_context():
        if Film.query.first() is not None:
            print("Database already seeded — nothing to do.")
            return

        demo = User(username="demo", email="demo@cinelog.dev")
        db.session.add(demo)
        for title, year, director, genre in FILMS:
            db.session.add(Film(title=title, year=year, director=director, genre=genre))
        db.session.commit()
        print(f"Seeded {len(FILMS)} films and user 'demo' (user_id: {demo.id}).")


if __name__ == "__main__":
    seed()
