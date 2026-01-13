from flask import Blueprint, request, current_app
from flask_restx import Api, Resource
from utils.db import get_db

occupancy_bp = Blueprint('occupancy', __name__)
api = Api(occupancy_bp, title='Occupancy Statistics API')

@api.route('/occupancy')
class OccupancyResource(Resource):
    def get(self):
        try:
            city = request.args.get('city')
            neighbourhood = request.args.get('neighbourhood')
            level = request.args.get('level')
            
            if city and city.lower() not in ['amsterdam', 'prague', 'rome']:
                return {'error': 'City must be amsterdam, prague, or rome'}, 400
            
            # Build cache key
            cache_key = f'occupancy_{city}_{neighbourhood}_{level}'
            cache = current_app.cache
            
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Build query
            query = {}
            if city:
                query['city'] = city
            if neighbourhood:
                query['neighbourhood'] = neighbourhood
            if level:
                query['level'] = level
            
            db = get_db()
            results = list(db.occupancy_by_month.find(query, {'_id': 0}))
            
            if not results:
                return [], 404
            
            # Cache for 10 minutes
            cache.set(cache_key, results, timeout=600)
            
            return results
            
        except Exception as e:
            return {'error': f'Query failed: {str(e)}'}, 500
