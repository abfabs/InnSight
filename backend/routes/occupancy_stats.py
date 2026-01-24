from flask import request, current_app
from flask_restx import Namespace, Resource
from utils.db import get_db

ns = Namespace("occupancy", path="/api/occupancy", description="Occupancy endpoints")

ALLOWED_CITIES = {"amsterdam", "rome", "prague", "sicily", "bordeaux", "crete"}
ALLOWED_LEVELS = {"city", "neighborhood"}


@ns.route("")
class OccupancyResource(Resource):
    def get(self):
        """
        Query params:
          - city: amsterdam|prague|rome|bordeaux|sicily|crete (optional)
          - level: city|neighborhood (default=city)
          - neighborhood: optional (only used when level=neighborhood)
        """
        try:
            city = request.args.get("city")
            level = request.args.get("level", "city")
            neighborhood = request.args.get("neighborhood")

            if level not in ALLOWED_LEVELS:
                return {"error": "Level must be city or neighborhood"}, 400

            if city:
                city = city.lower()
                if city not in ALLOWED_CITIES:
                    return {"error": "City must be amsterdam, prague, crete, sicily, bordeaux or rome"}, 400

            # Normalize cache key after lowercasing
            cache_key = f"occupancy_{city}_{neighborhood}_{level}"
            cache = current_app.cache

            cached = cache.get(cache_key)
            if cached:
                return cached, 200

            query = {"level": level}
            if city:
                query["city"] = city

            # Only apply neighborhood filter for neighborhood level
            if level == "neighborhood" and neighborhood:
                query["neighborhood"] = neighborhood

            db = get_db()

            if level == "city":
                doc = db.occupancy_by_month.find_one(query, {"_id": 0})
                results = [doc] if doc else []
            else:
                results = list(
                    db.occupancy_by_month
                      .find(query, {"_id": 0})
                      .sort([("neighborhood", 1)])
                )

            cache.set(cache_key, results, timeout=600)
            return results, 200

        except Exception as e:
            return {"error": f"Query failed: {str(e)}"}, 500
