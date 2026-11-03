"""
routes/watchlist.py — CineLog (feature/watchlist branch)

Endpoints for the watchlist feature.
"""

from flask import Blueprint, jsonify, request
<<<<<<< HEAD
from services.watchlist_service import (
    AlreadyOnWatchlistError,
    add_to_watchlist,
    get_watchlist,
)
=======
from services.watchlist_service import save_to_watchlist, get_watchlist
>>>>>>> af28e3c17551c9214411d8ff0f9972fabbae4029
from services.collection_service import FilmNotFoundError

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/<user_id>", methods=["GET"])
def view_watchlist(user_id):
    """GET /watchlist/<user_id> — Return the user's watchlist."""
    films = get_watchlist(user_id)
    return jsonify(films)


@watchlist_bp.route("/<user_id>/add", methods=["POST"])
def add_film(user_id):
    """
    POST /watchlist/<user_id>/add

<<<<<<< HEAD
    Body: { "film_id": "<uuid>" }
=======
    Body: { "film_id": <int> }
>>>>>>> af28e3c17551c9214411d8ff0f9972fabbae4029
    """
    data = request.get_json()
    if not data or "film_id" not in data:
        return jsonify({"error": "film_id is required"}), 400

<<<<<<< HEAD
    try:
        entry = add_to_watchlist(user_id=user_id, film_id=data["film_id"])
        return jsonify(entry.to_dict()), 201
    except AlreadyOnWatchlistError as e:
        return jsonify({"error": str(e)}), 409
=======
    entry = save_to_watchlist(user_id=user_id, film_id=data["film_id"])
    return jsonify(entry.to_dict()), 201
>>>>>>> af28e3c17551c9214411d8ff0f9972fabbae4029
