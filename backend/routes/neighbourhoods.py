from flask import Blueprint, request, current_app
from flask_restx import Api, Resource
from utils.db import get_db



neighbourhoods_bp = Blueprint('neighbourhoods', __name__)
api = Api(neighbourhoods_bp)



@api.route('/neighbourhoods')
class NeighbourhoodsResource(Resource):
    def get(self):
        try:
            city = request.args.get('city', 'prague')
            if not city or city.lower() not in ['amsterdam', 'prague', 'rome']:
                city = 'prague'
            
            # Build cache key
            cache_key = f'neighbourhoods_{city}'
            cache = current_app.cache
            
            # Check cache
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Query database if not cached
            db = get_db()
            
            # Query REAL neighborhood data from MongoDB
            neighbourhoods = list(
                db.listings_clean.distinct(
                    'neighbourhood', 
                    {'city': city, 'neighbourhood': {'$ne': None}}
                )
            )
            
            # Remove None/empty and sort
            neighbourhoods = sorted([n for n in neighbourhoods if n])
            
            result = {
                'neighbourhoods': neighbourhoods,
                'city': city,
                'total': len(neighbourhoods)
            }
            
            # Cache for 15 minutes (neighborhoods don't change)
            cache.set(cache_key, result, timeout=900)
            
            return result
            
        except Exception as e:
            return {'error': f'Neighborhood query failed: {str(e)}'}, 500
