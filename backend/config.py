import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'inn-sight-dev-key'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017'
