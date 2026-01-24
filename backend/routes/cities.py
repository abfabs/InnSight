from flask import current_app
from flask_restx import Namespace, Resource

ns = Namespace("cities", path="/api/cities", description="City endpoints")


@ns.route("")
class CitiesResource(Resource):
    def get(self):
        cache = current_app.cache

        cached = cache.get("cities_list")
        if cached:
            return cached, 200

        result = {"cities": ["amsterdam", "rome", "prague", "sicily", "bordeaux", "crete"]}

        # Cache for 10 minutes
        cache.set("cities_list", result, timeout=600)

        return result, 200
