from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from utils.db import get_db



wordcloud_bp = Blueprint('wordcloud', __name__)
api = Api(wordcloud_bp)



word_model = api.model('WordCloud', {
    'city': fields.String,
    'neighbourhood': fields.String,
    'word': fields.String,
    'frequency': fields.Integer
})



@api.route('/wordcloud')
class WordCloudResource(Resource):
    @api.marshal_with(word_model, as_list=True, skip_none=True)
    def get(self):
        # SAFE parameter parsing
        try:
            city = request.args.get('city', 'prague')
            if city and city.lower() not in ['amsterdam', 'prague', 'rome']:
                return {'error': 'City must be amsterdam, prague, or rome'}, 400
            
            neigh = request.args.get('neighbourhood')
            limit = int(request.args.get('limit', 20))
            
            if limit > 100:
                limit = 100  # Sanity limit for wordclouds
            
        except ValueError:
            return {'error': 'Invalid limit parameter (must be number)'}, 400
        
        # Build cache key with all parameters
        cache_key = f'wordcloud_{city}_{neigh if neigh else "all"}_{limit}'
        cache = current_app.cache
        
        # Check cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Query database if not cached
        db = get_db()
        query = {'city': city}
        if neigh:
            query['neighbourhood'] = neigh
        
        try:
            cursor = db.review_words.find(query).sort('frequency', -1).limit(limit)
            results = list(cursor)
            
            if not results:
                return [], 404
            
            # Cache for 15 minutes (word frequencies are static)
            cache.set(cache_key, results, timeout=900)
            
            return results
            
        except Exception as e:
            return {'error': f'Wordcloud query failed: {str(e)}'}, 500
