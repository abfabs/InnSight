from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from utils.db import get_db


rs_bp = Blueprint('reviews_sentiment', __name__)
api = Api(rs_bp)


rs_model = api.model('ReviewSentiment', {
    'listing_id': fields.String,
    'date': fields.String,
    'sentiment': fields.Float,
    'sentiment_category': fields.String
})


@api.route('/reviews-sentiment')
class RSResource(Resource):
    @api.marshal_with(rs_model, as_list=True)
    def get(self):
        db = get_db()
        
        # SAFE parameter parsing
        try:
            city = request.args.get('city')
            if city and city.lower() not in ['amsterdam', 'prague', 'rome']:
                return {'error': 'City must be amsterdam, prague, or rome'}, 400
            
            limit = int(request.args.get('limit', 1000))
            if limit > 5000:
                limit = 5000  # Sanity limit
            
        except ValueError:
            return {'error': 'Invalid limit parameter (must be number)'}, 400
        
        query = {'city': city} if city else {}
        
        try:
            # FIXED: upload collection + sort field
            cursor = db.reviews_sentiment.find(query).sort('date', -1).limit(limit)
            results = list(cursor)
            
            if not results:
                return [], 404
            
            return results
            
        except Exception as e:
            return {'error': f'Reviews query failed: {str(e)}'}, 500
