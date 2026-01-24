from flask import request, current_app
from flask_restx import Namespace, Resource
from utils.db import get_db

ns = Namespace("wordcloud", path="/api/wordcloud", description="Wordcloud endpoints")


def _image_url(city: str, neighborhood: str | None) -> str:
    """
    Matches your existing static route:
      /static/wordclouds/<city>/<filename>

    Your ETL saved:
      - neighborhood images: "<Neighborhood>.png"
      - city image: "<city>_overall.png"
    """
    if neighborhood:
        filename = f"{neighborhood}.png"
    else:
        filename = f"{city}_overall.png"
    return f"/static/wordclouds/{city}/{filename}"


@ns.route("")
class WordCloudResource(Resource):
    def get(self):
        """
        Query params:
          - city: aamsterdam|prague|rome|bordeaux|sicily|crete (default=prague)
          - neighborhood: optional
          - limit: optional (default=20, max=100)
        Returns:
          {
            city,
            neighborhood,
            image_url,
            words: [{word, frequency, neighborhood, city}, ...]
          }
        """
        try:
            city = request.args.get("city", "prague")
            if city and city.lower() not in ["amsterdam", "rome", "prague", "sicily", "bordeaux", "crete"]:
                return {"error": "City must be amsterdam, prague, sicily, bordeaux, crete or rome"}, 400

            neighborhood = request.args.get("neighborhood")
            limit = int(request.args.get("limit", 20))
            if limit > 100:
                limit = 100
            if limit < 1:
                limit = 1

        except ValueError:
            return {"error": "Invalid limit parameter (must be number)"}, 400

        cache_key = f"wordcloud_{city}_{neighborhood if neighborhood else 'all'}_{limit}"
        cache = current_app.cache

        cached = cache.get(cache_key)
        if cached:
            return cached, 200

        db = get_db()

        query = {"city": city}
        if neighborhood:
            query["neighborhood"] = neighborhood
        else:
            # city-level words are stored with neighborhood: None in your ETL
            query["neighborhood"] = None

        try:
            cursor = db.review_words.find(query, {"_id": 0}).sort("frequency", -1).limit(limit)
            words = list(cursor)

            result = {
                "city": city,
                "neighborhood": neighborhood,
                "image_url": _image_url(city, neighborhood),
                "words": words
            }

            cache.set(cache_key, result, timeout=900)
            return result, 200

        except Exception as e:
            return {"error": f"Wordcloud query failed: {str(e)}"}, 500
