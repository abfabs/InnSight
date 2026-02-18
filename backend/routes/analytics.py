from flask import request, current_app
from flask_restx import Namespace, Resource
from utils.db import get_db
from config import Config

ns = Namespace("analytics", path="/api/analytics", description="General analytics overview")


@ns.route("")
class AnalyticsResource(Resource):
    def get(self):
        """
        Query params:
          - city: amsterdam|lisbon|rome|bordeaux|sicily|crete (optional)
        Returns:
          list of city overview objects (one per city),
          or one object if city is provided.
        """
        # Parse city
        city = request.args.get("city")
        if city and city.lower() not in Config.ALLOWED_CITIES:
            return {"error": "Invalid city"}, 400


        cache_key = f"analytics_{city if city else 'all'}"
        cache = current_app.cache

        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        db = get_db()

        match_stage = {"price": {"$ne": None}}
        if city:
            match_stage["city"] = city

        try:
            # Basic city overview (fast, no giant arrays)
            pipeline = [
                {"$match": match_stage},
                {"$group": {
                    "_id": "$city",
                    "listing_count": {"$sum": 1},
                    "avg_price": {"$avg": "$price"}
                }},
                {"$project": {
                    "_id": 0,
                    "city": "$_id",
                    "listing_count": 1,
                    "avg_price": {"$round": ["$avg_price", 2]}
                }},
                {"$sort": {"listing_count": -1}}
            ]

            results = list(db.listings_clean.aggregate(pipeline))

            # Add top neighborhood only when city is specified
            if city:
                top_neigh = list(db.listings_clean.aggregate([
                    {"$match": {**match_stage, "neighborhood": {"$ne": None}}},
                    {"$group": {"_id": "$neighborhood", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 1}
                ]))

                if results:
                    if top_neigh:
                        results[0]["top_neighborhood"] = top_neigh[0]["_id"]
                        results[0]["top_neigh_count"] = int(top_neigh[0]["count"])
                    else:
                        results[0]["top_neighborhood"] = None
                        results[0]["top_neigh_count"] = 0

            cache.set(cache_key, results, timeout=300)
            return results, 200

        except Exception as e:
            return {"error": f"Analytics query failed: {str(e)}"}, 500
