from flask import request, current_app
from flask_restx import Namespace, Resource
from utils.db import get_db
from config import Config
import math

ns = Namespace("listings", path="/api", description="Listings and map endpoints")


def _clean_nan(v):
    return None if isinstance(v, float) and math.isnan(v) else v


def _clean_doc(doc: dict) -> dict:
    # drop mongo _id so frontend doesn't see it
    doc.pop("_id", None)

    for key in [
        "price",
        "latitude",
        "longitude",
        "sentiment_mean",
        "review_count",
        "number_of_reviews",
        "review_scores_rating",
    ]:
        if key in doc:
            doc[key] = _clean_nan(doc[key])

    return doc


def _validate_city(city: str | None):
    if city and city.lower() not in Config.ALLOWED_CITIES:
        return False
    return True



@ns.route("/listings")
class ListingsResource(Resource):
    def get(self):
        """
        Full listings (used for list/table and also OK for map).
        Query params:
          - city (optional but recommended): amsterdam|lisbon|rome|bordeaux|sicily|crete
          - neighborhood (optional)
          - room_type (optional)
          - min_price (optional)
          - max_price (optional)
          - limit (optional, default=500, max=50000)
        """
        db = get_db()

        try:
            city = request.args.get("city")
            neighborhood = request.args.get("neighborhood", "")
            min_price = request.args.get("min_price")
            max_price = request.args.get("max_price")
            room_type = request.args.get("room_type")
            limit = int(request.args.get("limit", 500))

            if not _validate_city(city):
                return {"error": "Invalid city"}, 400

            if min_price is not None:
                min_price = float(min_price)
                if min_price < 0:
                    return {"error": "min_price must be >= 0"}, 400

            if max_price is not None:
                max_price = float(max_price)
                if max_price < 0:
                    return {"error": "max_price must be >= 0"}, 400

            if limit > 50000:
                limit = 50000
            if limit < 0:
                limit = 0

        except ValueError as e:
            return {"error": f"Invalid parameter: {str(e)}"}, 400

        cache_key = f"listings_{city}_{neighborhood}_{min_price}_{max_price}_{room_type}_{limit}"
        cache = current_app.cache

        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        query = {}

        if city:
            query["city"] = city

        if neighborhood:
            query["neighborhood"] = neighborhood

        if room_type:
            query["room_type"] = room_type

        if min_price is not None or max_price is not None:
            query["price"] = {}
            if min_price is not None:
                query["price"]["$gte"] = min_price
            if max_price is not None:
                query["price"]["$lte"] = max_price

        try:
            cursor = db.listings_map.find(query, {"_id": 0})  # exclude _id at query-time

            if limit and limit > 0:
                cursor = cursor.limit(limit)

            results = [_clean_doc(doc) for doc in cursor]

            cache.set(cache_key, results, timeout=300)
            return results, 200

        except Exception as e:
            print(f"❌ listings query error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": f"Database query failed: {str(e)}"}, 500


@ns.route("/listings-map")
class ListingsMapResource(Resource):
    def get(self):
        """
        Lightweight listings for map markers.
        Same filters as /listings, but defaults to a higher limit.
        Query params:
          - city (required for performance)
          - neighborhood (optional)
          - limit (optional, default=5000, max=50000)
        """
        # reuse ListingsResource logic by calling it with a different default limit
        # (keep it simple, no duplication)
        args = request.args.to_dict(flat=True)
        if "limit" not in args:
            args["limit"] = "5000"

        # Monkey-patch request args is messy; just re-run query with the smaller filter set
        db = get_db()

        city = args.get("city")
        neighborhood = args.get("neighborhood", "")
        limit = int(args.get("limit", 5000))

        if not city:
            return {"error": "city required"}, 400
        if not _validate_city(city):
            return {"error": "Invalid city"}, 400
        if limit > 50000:
            limit = 50000
        if limit < 0:
            limit = 0

        cache_key = f"listings_map_{city}_{neighborhood}_{limit}"
        cache = current_app.cache
        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        query = {"city": city}
        if neighborhood:
            query["neighborhood"] = neighborhood

        try:
            # Only fields needed for map markers + tooltip
            projection = {
                "_id": 0,
                "listing_id": 1,
                "listing_name": 1,
                "latitude": 1,
                "longitude": 1,
                "price": 1,
                "room_type": 1,
                "neighborhood": 1,
                "sentiment_mean": 1,
                "sentiment_category": 1,
                "review_count": 1,
                "city": 1,
            }

            cursor = db.listings_map.find(query, projection).limit(limit) if limit else db.listings_map.find(query, projection)
            results = [_clean_doc(doc) for doc in cursor]

            cache.set(cache_key, results, timeout=300)
            return results, 200

        except Exception as e:
            print(f"❌ listings-map query error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": f"Database query failed: {str(e)}"}, 500
