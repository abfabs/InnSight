from flask import Blueprint, current_app
from flask_restx import Api, Resource


cities_bp = Blueprint('cities', __name__)
api = Api(cities_bp)


@api.route('/cities')
class CitiesResource(Resource):
    def get(self):
        cache = current_app.cache
        
        # Check cache
        cached = cache.get('cities_list')
        if cached:
            return cached
        
        # Build response
        result = {'cities': ['prague', 'rome', 'amsterdam']}
        
        # Cache for 10 minutes (this data never changes)
        cache.set('cities_list', result, timeout=600)
        
        return result
