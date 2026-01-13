from flask import Blueprint, request, current_app
from flask_restx import Api, Resource
from utils.db import get_db

room_types_bp = Blueprint('room_types', __name__)
api = Api(room_types_bp, title='Room Type Distribution API')

@api.route('/room-types')
class RoomTypesResource(Resource):
    def get(self):
        try:
            city = request.args.get('city')
            neighbourhood = request.args.get('neighbourhood')
            level = request.args.get('level')
            
            if city and city.lower() not in ['amsterdam', 'prague', 'rome']:
                return {'error': 'City must be amsterdam, prague, or rome'}, 400
            
            # Build cache key
            cache_key = f'room_types_{city}_{neighbourhood}_{level}'
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
            results = list(db.room_type_distribution.find(query, {'_id': 0}).sort('total_listings', -1))
            
            if not results:
                return [], 404
            
            # Cache for 10 minutes
            cache.set(cache_key, results, timeout=600)
            
            return results
            
        except Exception as e:
            return {'error': f'Query failed: {str(e)}'}, 500
