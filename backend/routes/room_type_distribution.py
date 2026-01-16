from flask import request, current_app
from flask_restx import Namespace, Resource
from utils.db import get_db

ns = Namespace("room_types", path="/api/room-types", description="Room type distribution endpoints")


@ns.route("")
class RoomTypesResource(Resource):
    def get(self):
        """
        Query params:
          - city: amsterdam|prague|rome (optional)
          - level: city|neighborhood (optional)
          - neighborhood: optional (for level=neighborhood)
        """
        try:
            city = request.args.get("city")
            neighborhood = request.args.get("neighborhood")
            level = request.args.get("level")

            if city and city.lower() not in ["amsterdam", "prague", "rome"]:
                return {"error": "City must be amsterdam, prague, or rome"}, 400

            cache_key = f"room_types_{city}_{neighborhood}_{level}"
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
                db.room_type_distribution
                  .find(query, {"_id": 0})
                  .sort("total_listings", -1)
            )

            # return empty list with 200 for frontend simplicity
            cache.set(cache_key, results, timeout=600)
            return results, 200

        except Exception as e:
            return {"error": f"Query failed: {str(e)}"}, 500
