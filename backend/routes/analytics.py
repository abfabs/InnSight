from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from utils.db import get_db



analytics_bp = Blueprint('analytics', __name__)
api = Api(analytics_bp, title='Analytics API', description='InnSight price/neighborhood stats')



stats_model = api.model('CityStats', {
    'city': fields.String,
    'listing_count': fields.Integer,
    'avg_price': fields.Float,
    'price_25p': fields.Float, 'price_50p': fields.Float, 'price_75p': fields.Float,
    'top_neighbourhood': fields.String, 'top_neigh_count': fields.Integer
})



@api.route('/analytics')
class AnalyticsResource(Resource):
    @api.marshal_with(stats_model, as_list=True)
    @api.expect({'city': fields.String(default=None)})
    def get(self):
        # Parse city parameter
        try:
            city = request.args.get('city')
            if not city or city.lower() not in ['amsterdam', 'prague', 'rome']:
                city = None
        except Exception:
            return {'error': 'Invalid city parameter'}, 400
        
        # Create cache key based on city parameter
        cache_key = f'analytics_{city if city else "all"}'
        cache = current_app.cache
        
        # Try to get from cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # If not cached, run the expensive query
        db = get_db()
        match_stage = {'price': {'$gte': 0}}
        if city:
            match_stage['city'] = city
        
        try:
            # FIXED: Query listings_clean (snake_case)
            overview_pipeline = [
                {'$match': match_stage},
                {'$group': {'_id': '$city', 'listing_count': {'$sum': 1}, 'avg_price': {'$avg': '$price'}, 'prices': {'$push': '$price'}}},
                {'$addFields': {
                    'price_25p': {'$arrayElemAt': [{'$sortArray': {'input': '$prices', 'sortBy': 1}}, {'$floor': {'$multiply': [{'$size': '$prices'}, 0.25]}}]},
                    'price_50p': {'$arrayElemAt': [{'$sortArray': {'input': '$prices', 'sortBy': 1}}, {'$floor': {'$multiply': [{'$size': '$prices'}, 0.5]}}]},
                    'price_75p': {'$arrayElemAt': [{'$sortArray': {'input': '$prices', 'sortBy': 1}}, {'$floor': {'$multiply': [{'$size': '$prices'}, 0.75]}}]}
                }},
                {'$project': {'prices': 0}},
                {'$sort': {'listing_count': -1}}
            ]
            results = list(db.listings_clean.aggregate(overview_pipeline))
            
            if not results:
                return [], 404
            
            # Robust fallback if percentiles fail (large arrays)
            if results[0].get('listing_count') is None:
                results[0]['listing_count'] = db.listings_clean.count_documents(match_stage)
            if results[0].get('avg_price') is None:
                avg_result = list(db.listings_clean.aggregate([
                    {'$match': match_stage}, 
                    {'$group': {'_id': None, 'avg': {'$avg': '$price'}}}
                ]))
                results[0]['avg_price'] = avg_result[0]['avg'] if avg_result else 0
            
            if city:
                top_neigh_pipeline = [
                    {'$match': match_stage},
                    {'$match': {'neighbourhood': {'$ne': None}}},
                    {'$group': {'_id': '$neighbourhood', 'count': {'$sum': 1}}},
                    {'$sort': {'count': -1}}, {'$limit': 1}
                ]
                top_neigh = list(db.listings_clean.aggregate(top_neigh_pipeline))
                if top_neigh:
                    results[0]['top_neighbourhood'] = top_neigh[0]['_id']
                    results[0]['top_neigh_count'] = top_neigh[0]['count']
            
            # Cache the results for 5 minutes (300 seconds)
            cache.set(cache_key, results, timeout=300)
            
            return results
            
        except Exception as e:
            return {'error': f'Analytics query failed: {str(e)}'}, 500
