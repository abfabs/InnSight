# backend/utils/db.py

from pymongo import MongoClient
from flask import current_app
import os

def get_db():
    """Returns MongoDB connection from app config."""
    return current_app.config['MONGO_DB']

def init_db(app):
    """Initialize MongoDB connection in Flask app."""
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    client = MongoClient(app.config['MONGO_URI'])
    app.config['MONGO_CLIENT'] = client
    app.config['MONGO_DB'] = client.innsight_db
    
    # Auto-create indexes for perf (listings geo, filters)
    db = app.config['MONGO_DB']
    # FIXED: Use snake_case collection names to match CSV uploads
    db.listings_clean.create_index([("location", "2dsphere")])
    db.listings_clean.create_index([("city", 1), ("neighbourhood", 1)])
    db.listings_clean.create_index([("city", 1), ("price", 1)])
    db.neighborhood_sentiment.create_index([("city", 1)])
    print("✅ MongoDB connected + indexes created (innsight_db)")

