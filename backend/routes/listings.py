from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from utils.db import get_db


listings_bp = Blueprint('listings', __name__)
api = Api(listings_bp)

# Flask-RESTX fields model (works with marshal_with)
listing_model = api.model('Listing', {
    'listing_id': fields.String,
    'listing_name': fields.String,
    'host_name': fields.String,
    'neighbourhood': fields.String,
    'latitude': fields.Float,
    'longitude': fields.Float,
    'room_type': fields.String,
    'price': fields.Float,
    'number_of_reviews': fields.Integer,
    'review_scores_rating': fields.Float,
    'sentiment_mean': fields.Float
})


@api.route('/listings')
class ListingsResource(Resource):
    @api.marshal_with(listing_model, as_list=True)
    def get(self):
        db = get_db()
        
        # SAFE parameter parsing with error handling
        try:
            city = request.args.get('city')
            neigh = request.args.get('neighbourhood')
            min_price = request.args.get('min_price')
            max_price = request.args.get('max_price')
            room_type = request.args.get('room_type')
            limit = int(request.args.get('limit', 500))
            
            # Validate numeric params
            if min_price is not None:
                min_price = float(min_price)
                if min_price < 0:
                    return {'error': 'min_price must be >= 0'}, 400
            
            if max_price is not None:
                max_price = float(max_price)
                if max_price < 0:
                    return {'error': 'max_price must be >= 0'}, 400
            
            if limit > 1000:
                limit = 1000
            
        except ValueError:
            return {'error': 'Invalid numeric parameter (limit, min_price, max_price)'}, 400
        
        # Build match query
        match_query = {'price': {'$gte': 0}}
        if city:
            match_query['city'] = city
        if neigh:
            match_query['neighbourhood'] = neigh
        if min_price is not None:
            match_query['price']['$gte'] = min_price
        if max_price is not None:
            match_query.setdefault('price', {})['$lte'] = max_price
        if room_type:
            match_query['room_type'] = room_type
        
        try:
            pipeline = [
                {'$match': match_query},
                {'$lookup': {
                    'from': 'listing_sentiment',
                    'localField': 'listing_id',
                    'foreignField': 'listing_id',
                    'as': 'sentiment'
                }},
                {'$addFields': {
                    'sentiment_mean': {'$ifNull': [{'$arrayElemAt': ['$sentiment.sentimentmean', 0]}, 0.0]}
                }},
                {'$project': {
                    'listing_id': {'$ifNull': ['$listing_id', '$listingid']},
                    'listing_name': {'$ifNull': ['$listing_name', '$listingname', 'Unnamed']},
                    'host_name': {'$ifNull': ['$host_name', '$hostname', 'Unknown']},
                    'neighbourhood': {'$ifNull': ['$neighbourhood', 'Unknown']},
                    'latitude': 1,
                    'longitude': 1,
                    'room_type': {'$ifNull': ['$room_type', '$roomtype']},
                    'price': 1,
                    'number_of_reviews': {'$ifNull': ['$number_of_reviews', '$numberofreviews', 0]},
                    'review_scores_rating': {'$ifNull': ['$review_score_rating', '$reviewscorerating', 0.0]},
                    'sentiment_mean': 1
                }},
                {'$limit': limit},
                {'$sort': {'price': 1}}
            ]
            
            results = list(db.listings_clean.aggregate(pipeline))
            return results
            
        except Exception as e:
            return {'error': f'Database query failed: {str(e)}'}, 500
