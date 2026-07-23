"""
extensions.py — CineLog

Shared Flask extension instances. The single SQLAlchemy instance lives here so
that every module — and `python app.py` itself — uses the same one.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
