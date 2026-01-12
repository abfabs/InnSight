from flask import Blueprint, request
from flask_restx import Api, Resource
from utils.db import get_db


neighbourhoods_bp = Blueprint('neighbourhoods', __name__)
api = Api(neighbourhoods_bp)


@api.route('/neighbourhoods')
class NeighbourhoodsResource(Resource):
    def get(self):
        db = get_db()
        
        try:
            city = request.args.get('city', 'prague')
            if not city or city.lower() not in ['amsterdam', 'prague', 'rome']:
                city = 'prague'
            
            # Query REAL neighborhood data from MongoDB
            neighbourhoods = list(
                db.listings_clean.distinct(
                    'neighbourhood', 
                    {'city': city, 'neighbourhood': {'$ne': None}}
                )
            )
            
            # Remove None/empty and sort
            neighbourhoods = sorted([n for n in neighbourhoods if n])
            
            return {
                'neighbourhoods': neighbourhoods,
                'city': city,
                'total': len(neighbourhoods)
            }
            
        except Exception as e:
            return {'error': f'Neighborhood query failed: {str(e)}'}, 500
