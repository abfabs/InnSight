from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from utils.db import get_db

sentiment_summary_bp = Blueprint('sentiment_summary', __name__)
api = Api(sentiment_summary_bp, title='Sentiment Summary API')

sentiment_model = api.model('SentimentSummary', {
    'city': fields.String,
    'neighbourhood': fields.String,
    'level': fields.String,
    'sentiment_mean': fields.Float,
    'sentiment_median': fields.Float,
    'total_reviews': fields.Integer,
    'positive': fields.Float,
    'neutral': fields.Float,
    'negative': fields.Float
})

@api.route('/sentiment-summary')
class SentimentSummaryResource(Resource):
    @api.marshal_with(sentiment_model, as_list=True)
    def get(self):
        try:
            city = request.args.get('city')
            neighbourhood = request.args.get('neighbourhood')
            level = request.args.get('level')  # 'city' or 'neighbourhood'
            
            if city and city.lower() not in ['amsterdam', 'prague', 'rome']:
                return {'error': 'City must be amsterdam, prague, or rome'}, 400
            
            # Build cache key
            cache_key = f'sentiment_summary_{city}_{neighbourhood}_{level}'
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
            results = list(db.sentiment_summary.find(query, {'_id': 0}).sort('sentiment_mean', -1))
            
            if not results:
                return [], 404
            
            # Cache for 10 minutes
            cache.set(cache_key, results, timeout=600)
            
            return results
            
        except Exception as e:
            return {'error': f'Query failed: {str(e)}'}, 500
