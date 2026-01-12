from flask import Blueprint
from flask_restx import Api, Resource

cities_bp = Blueprint('cities', __name__)
api = Api(cities_bp)

@api.route('/cities')
class CitiesResource(Resource): 
    def get(self):
        return {'cities': ['prague', 'rome', 'amsterdam']}
