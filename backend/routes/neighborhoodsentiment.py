from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from utils.db import get_db


ns_bp = Blueprint('neighborhoodsentiment', __name__)
api = Api(ns_bp)


ns_model = api.model('NeighborhoodSentiment', {
    'neighbourhood': fields.String,
    'sentiment_mean': fields.Float,
    'sentiment_median': fields.Float,
    'total_reviews': fields.Integer,
    'positive': fields.Float,
    'neutral': fields.Float,
    'negative': fields.Float
})


@api.route('/neighborhood-sentiment')
class NSResource(Resource):
    @api.marshal_with(ns_model, as_list=True)
    def get(self):
        db = get_db()
        
        # SAFE parameter parsing
        try:
            city = request.args.get('city', 'amsterdam')
            if not city or city.lower() not in ['amsterdam', 'prague', 'rome']:
                city = 'amsterdam'  # Default to valid city
        except Exception:
            return {'error': 'Invalid city parameter'}, 400
        
        try:
            # FIXED: snake_case collection + field
            cursor = db.neighborhood_sentiment.find({'city': city}).sort('sentimentmean', -1)
            results = list(cursor)
            
            if not results:
                return [], 404
            
            return results
            
        except Exception as e:
            return {'error': f'Sentiment query failed: {str(e)}'}, 500
