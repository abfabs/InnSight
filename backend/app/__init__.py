from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
from config import Config
import os



# Core routes
from routes.listings import listings_bp
from routes.analytics import analytics_bp
from routes.neighbourhoods import neighbourhoods_bp
from routes.wordcloud import wordcloud_bp
from routes.cities import cities_bp

# Sentiment routes 
from routes.neighborhoodsentiment import ns_bp
from routes.reviews_sentiment import rs_bp

# Dashboard analytics routes
from routes.sentiment_summary import sentiment_summary_bp
from routes.room_type_distribution import room_types_bp
from routes.occupancy_stats import occupancy_bp
from routes.top_hosts_route import top_hosts_bp

from utils.db import init_db



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for React frontend
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize cache
    cache = Cache(app, config={
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes default
    })
    app.cache = cache  # Make cache accessible to routes via current_app.cache
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    app.register_blueprint(cities_bp, url_prefix='/api')
    app.register_blueprint(listings_bp, url_prefix='/api')
    app.register_blueprint(neighbourhoods_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(wordcloud_bp, url_prefix='/api')
    app.register_blueprint(ns_bp, url_prefix='/api')
    app.register_blueprint(rs_bp, url_prefix='/api')
    
    # Dashboard analytics routes
    app.register_blueprint(sentiment_summary_bp, url_prefix='/api')
    app.register_blueprint(room_types_bp, url_prefix='/api')
    app.register_blueprint(occupancy_bp, url_prefix='/api')
    app.register_blueprint(top_hosts_bp, url_prefix='/api')
    
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
