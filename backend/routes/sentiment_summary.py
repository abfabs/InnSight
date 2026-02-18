from flask import request
from flask_restx import Namespace, Resource
from utils.db import get_db
from config import Config
import math

ns = Namespace("sentiment_summary", path="/api/sentiment-summary", description="Sentiment summary endpoints")

ALLOWED_LEVELS = {"city", "neighborhood"}


def _clean_numbers(results):
    """Clean NaNs + enforce numeric types on count fields."""
    for r in results:
        # percent fields
        for k in ["positive", "neutral", "negative"]:
            v = r.get(k)
            if isinstance(v, float) and math.isnan(v):
                r[k] = None

        # count fields
        for k in ["total_reviews", "positive_count", "neutral_count", "negative_count"]:
            v = r.get(k)
            if isinstance(v, float) and math.isnan(v):
                r[k] = 0
            if v is not None:
                try:
                    r[k] = int(v)
                except Exception:
                    r[k] = 0

    return results


@ns.route("")
class SentimentSummaryResource(Resource):
    def get(self):
        """
        Query params:
          - city: amsterdam|lisbon|rome|bordeaux|sicily|crete (optional)
          - level: city|neighborhood (default=city)
          - neighborhood: optional (only used when level=neighborhood)
        """
        try:
            city = request.args.get("city")
            neighborhood = request.args.get("neighborhood")
            level = request.args.get("level", "city")

            if level not in ALLOWED_LEVELS:
                return {"error": "Invalid level"}, 400

            if city:
                city = city.lower()
                if city not in Config.ALLOWED_CITIES:
                    return {"error": "Invalid city"}, 400

            query = {"level": level}
            if city:
                query["city"] = city

            # ✅ Only apply neighborhood filter for neighborhood level
            if level == "neighborhood" and neighborhood:
                query["neighborhood"] = neighborhood

            db = get_db()

            # ✅ For level=city, return a single doc (wrapped as list)
            if level == "city":
                doc = db.sentiment_summary.find_one(query, {"_id": 0})
                if not doc:
                    return [], 200
                results = [doc]
                return _clean_numbers(results), 200

            # Neighborhood level can return multiple docs
            results = list(
                db.sentiment_summary
                  .find(query, {"_id": 0})
                  .sort("total_reviews", -1)
            )

            results = _clean_numbers(results)
            return results, 200

        except Exception as e:
            print(f"sentiment-summary error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": "Query failed"}, 500
