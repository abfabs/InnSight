from flask import request, current_app
from flask_restx import Namespace, Resource
from utils.db import get_db
from config import Config
import math

ns = Namespace("top_hosts", path="/api/top-hosts", description="Top hosts endpoints")


def _clean_nan(obj):
    # top_hosts_agg may contain NaN from avg_rating; convert to None for JSON safety
    if isinstance(obj, float) and math.isnan(obj):
        return None
    if isinstance(obj, list):
        return [_clean_nan(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _clean_nan(v) for k, v in obj.items()}
    return obj


@ns.route("")
class TopHostsResource(Resource):
    def get(self):
        """
        Query params:
          - city: amsterdam|lisbon|rome|bordeaux|sicily|crete (optional)
          - level: city|neighborhood (optional)
          - neighborhood: optional (for level=neighborhood)
        """
        try:
            city = request.args.get("city")
            neighborhood = request.args.get("neighborhood")
            level = request.args.get("level")

            if city and city.lower() not in Config.ALLOWED_CITIES:
                return {"error": "City must be amsterdam, lisbon, sicily, bordeaux, crete or rome"}, 400

            cache_key = f"top_hosts_{city}_{neighborhood}_{level}"
            cache = current_app.cache

            cached = cache.get(cache_key)
            if cached:
                return cached, 200

            query = {}
            if city:
                query["city"] = city
            if neighborhood:
                query["neighborhood"] = neighborhood
            if level:
                query["level"] = level

            db = get_db()

            results = list(
                db.top_hosts_agg
                  .find(query, {"_id": 0})
                  .sort([("level", 1), ("neighborhood", 1)])
            )

            results = _clean_nan(results)

            cache.set(cache_key, results, timeout=600)
            return results, 200

        except Exception as e:
            return {"error": f"Query failed: {str(e)}"}, 500
