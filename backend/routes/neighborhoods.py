from flask import request
from flask_restx import Namespace, Resource
from utils.db import get_db
from config import Config

ns = Namespace("neighborhoods", path="/api/neighborhoods", description="Neighborhood endpoints")


@ns.route("")
class NeighborhoodsResource(Resource):
    def get(self):
        """
        Get neighborhoods for a city.
        Query params:
          - city (required): amsterdam|lisbon|rome|bordeaux|sicily|crete
        """
        try:
            city = request.args.get("city")
            if not city:
                return {"error": "city required"}, 400

            if city.lower() not in Config.ALLOWED_CITIES:
                return {"error": "Invalid city"}, 400

            db = get_db()

            neighborhoods = db.listings_clean.distinct(
                "neighborhood",
                {"city": city, "neighborhood": {"$ne": None}}
            )

            # Clean + sort
            cleaned = sorted([n for n in neighborhoods if isinstance(n, str) and n.strip()])

            return {"city": city, "neighborhoods": cleaned}, 200

        except Exception as e:
            return {"error": str(e)}, 500
