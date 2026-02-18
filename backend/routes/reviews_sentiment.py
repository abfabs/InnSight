from flask import request, current_app
from flask_restx import Namespace, Resource
from utils.db import get_db
from config import Config

ns = Namespace("reviews_sentiment", path="/api/reviews-sentiment", description="Review-level sentiment endpoints")


@ns.route("")
class ReviewsSentimentResource(Resource):
    def get(self):
        """
        Query params:
          - city: amsterdam|lisbon|rome|bordeaux|sicily|crete (optional but recommended)
          - limit: optional (default=1000, max=5000)
        Returns: list of review sentiment rows (most recent first)
        """
        try:
            city = request.args.get("city")
            if city and city.lower() not in Config.ALLOWED_CITIES:
                return {"error": "City must be amsterdam, lisbon, sicily, bordeaux, crete or rome"}, 400

            limit = int(request.args.get("limit", 1000))
            if limit > 5000:
                limit = 5000
            if limit < 1:
                limit = 1

        except ValueError:
            return {"error": "Invalid limit parameter (must be number)"}, 400

        cache_key = f"reviews_sentiment_{city if city else 'all'}_{limit}"
        cache = current_app.cache

        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        db = get_db()

        query = {"city": city} if city else {}

        try:
            cursor = (
                db.reviews_sentiment
                  .find(query, {"_id": 0})
                  .sort("date", -1)
                  .limit(limit)
            )
            results = list(cursor)

            cache.set(cache_key, results, timeout=300)
            return results, 200

        except Exception as e:
            return {"error": f"Reviews query failed: {str(e)}"}, 500
