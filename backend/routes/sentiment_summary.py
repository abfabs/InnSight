from flask import request
from flask_restx import Namespace, Resource
from utils.db import get_db
import math

ns = Namespace("sentiment_summary", path="/api/sentiment-summary", description="Sentiment summary endpoints")


@ns.route("")
class SentimentSummaryResource(Resource):
    def get(self):
        """
        Query params:
          - city: amsterdam|prague|rome (optional)
          - level: city|neighborhood (default=city)
          - neighborhood: optional (for level=neighborhood)
        """
        try:
            city = request.args.get("city")
            neighborhood = request.args.get("neighborhood")
            level = request.args.get("level", "city")

            if city and city.lower() not in ["amsterdam", "prague", "rome"]:
                return {"error": "Invalid city"}, 400

            query = {}
            if city:
                query["city"] = city
            if neighborhood:
                query["neighborhood"] = neighborhood
            if level:
                query["level"] = level

            db = get_db()

            # sentiment_summary now stores counts + percentages; sort by total_reviews
            results = list(
                db.sentiment_summary
                  .find(query, {"_id": 0})
                  .sort("total_reviews", -1)
            )

            # Clean NaN values & enforce numeric types
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

            return results, 200

        except Exception as e:
            print(f"sentiment-summary error: {e}")
            import traceback
            traceback.print_exc()
            return {"error": "Query failed"}, 500
