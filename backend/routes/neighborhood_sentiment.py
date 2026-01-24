from flask import request, current_app
from flask_restx import Namespace, Resource
from utils.db import get_db
import math

ns = Namespace(
    "neighborhood_sentiment",
    path="/api/neighborhood-sentiment",
    description="Neighborhood sentiment endpoints"
)

ALLOWED_CITIES = {"amsterdam", "rome", "prague", "sicily", "bordeaux", "crete"}


def _clean_nan(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, list):
        return [_clean_nan(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _clean_nan(v) for k, v in obj.items()}
    return obj


@ns.route("")
class NeighborhoodSentimentResource(Resource):
    def get(self):
        """
        Query params:
          - city: amsterdam|prague|rome|bordeaux|sicily|crete (default=amsterdam)

        Returns:
          list of neighborhood sentiment rows sorted by sentiment_mean desc
        """
        city = request.args.get("city", "amsterdam")
        if not city or city.lower() not in ALLOWED_CITIES:
            return {"error": "City must be amsterdam, prague, bordeaux, crete, sicily or rome"}, 400

        # ✅ Normalize once, use everywhere (query + cache)
        city = city.lower()

        cache_key = f"neighborhood_sentiment_{city}"
        cache = current_app.cache

        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        db = get_db()

        try:
            cursor = (
                db.neighborhood_sentiment
                  .find({"city": city}, {"_id": 0})
                  .sort("sentiment_mean", -1)
            )
            results = list(cursor)
            results = _clean_nan(results)

            cache.set(cache_key, results, timeout=600)
            return results, 200

        except Exception as e:
            return {"error": f"Sentiment query failed: {str(e)}"}, 500
