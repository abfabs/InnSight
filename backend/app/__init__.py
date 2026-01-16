from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
from config import Config
import os

from utils.db import init_db
from app.extensions import api

# Import RESTX namespaces
from routes.cities import ns as cities_ns
from routes.listings import ns as listings_ns
from routes.neighborhoods import ns as neighborhoods_ns
from routes.analytics import ns as analytics_ns
from routes.wordcloud import ns as wordcloud_ns

from routes.neighborhood_sentiment import ns as neighborhood_sentiment_ns
from routes.reviews_sentiment import ns as reviews_sentiment_ns

from routes.sentiment_summary import ns as sentiment_summary_ns
from routes.room_type_distribution import ns as room_type_distribution_ns
from routes.occupancy_stats import ns as occupancy_ns
from routes.top_hosts_route import ns as top_hosts_ns


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS for React frontend
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Initialize cache
    cache = Cache(app, config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 300  # 5 minutes default
    })
    app.cache = cache  # accessible via current_app.cache

    # Initialize database
    init_db(app)

    # Initialize RESTX API
    api.init_app(app)

    # Register namespaces
    api.add_namespace(cities_ns)
    api.add_namespace(listings_ns)
    api.add_namespace(neighborhoods_ns)
    api.add_namespace(analytics_ns)
    api.add_namespace(wordcloud_ns)

    api.add_namespace(neighborhood_sentiment_ns)
    api.add_namespace(reviews_sentiment_ns)

    api.add_namespace(sentiment_summary_ns)
    api.add_namespace(room_type_distribution_ns)
    api.add_namespace(occupancy_ns)
    api.add_namespace(top_hosts_ns)

    @app.route("/")
    def health_check():
        return {
            "status": "InnSight API LIVE ✅",
            "data_ready": True,
            "cities": ["amsterdam", "prague", "rome"],
            "endpoints": [
                "/api/listings?city=amsterdam",
                "/api/neighborhood-sentiment?city=rome",
                "/api/reviews-sentiment?city=prague&limit=100",
                "/static/wordclouds/prague/Praha_1.png"
            ]
        }

    # Serve wordcloud images
    @app.route("/static/wordclouds/<city>/<filename>")
    def serve_wordcloud(city, filename):
        """Serve wordcloud PNG images from processed data"""
        image_path = os.path.join(
            app.root_path, "..", "data", "processed", city, "wordcloud_images"
        )
        return send_from_directory(image_path, filename)

    return app
