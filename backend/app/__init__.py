from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
import os


# Core routes
from routes.listings import listings_bp
from routes.analytics import analytics_bp


# Stubs for missing
from routes.cities import cities_bp
from routes.neighbourhoods import neighbourhoods_bp
from routes.wordcloud import wordcloud_bp


# NEW sentiment routes 
from routes.neighborhoodsentiment import ns_bp
from routes.reviews_sentiment import rs_bp


from utils.db import init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for React frontend
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize database
    init_db(app)
    
    # Register blueprints (SAFE - stubs don't crash)
    app.register_blueprint(cities_bp, url_prefix='/api')
    app.register_blueprint(listings_bp, url_prefix='/api')
    app.register_blueprint(neighbourhoods_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(wordcloud_bp, url_prefix='/api')
    
    # NEW: Sentiment routes
    app.register_blueprint(ns_bp, url_prefix='/api')
    app.register_blueprint(rs_bp, url_prefix='/api')
    
    @app.route('/')
    def health_check():
        return {
            'status': 'InnSight API LIVE ✅',
            'data_ready': True,
            'cities': ['amsterdam', 'prague', 'rome'],
            'endpoints': [
                '/api/listings?city=amsterdam',
                '/api/neighborhood-sentiment?city=rome',
                '/api/reviews-sentiment?city=prague&limit=100',
                '/static/wordclouds/prague/Praha_1.png'
            ]
        }
    
    # Serve wordcloud images
    @app.route('/static/wordclouds/<city>/<filename>')
    def serve_wordcloud(city, filename):
        """Serve wordcloud PNG images from processed data"""
        image_path = os.path.join(
            app.root_path, '..', 'data', 'processed', city, 'wordcloud_images'
        )
        return send_from_directory(image_path, filename)
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
