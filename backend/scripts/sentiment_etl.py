#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import math


class SentimentETL:
    """
    Sentiment analysis on reviews using PROCESSED listings_clean.csv
    Requires: data_etl.py run first (creates listings_clean.csv)
    VADER only works on English - filters non-English reviews
    """

    def __init__(self, city):
        self.city = city
        self.raw_path = Path(f'../data/raw/{city}')
        self.processed_path = Path(f'../data/processed/{city}')
        self.processed_path.mkdir(parents=True, exist_ok=True)

        self.vader = SentimentIntensityAnalyzer()

    def is_likely_english(self, text):
        if pd.isna(text) or len(str(text)) < 10:
            return False

        text_lower = str(text).lower()

        non_english_markers = [
            'het', 'een', 'van', 'voor', 'was', 'zeer', 'erg', 'mooie', 'zijn', 'de', 'op',
            'sehr', 'gut', 'war', 'und', 'ist', 'auch', 'wir', 'schön', 'die', 'der',
            'molto', 'bella', 'ottimo', 'casa', 'bellissimo', 'siamo', 'che', 'della',
            'très', 'bien', 'nous', 'était', 'avec', 'merci', 'les', 'des',
            'muy', 'estaba', 'todo', 'casa', 'excelente', 'las', 'los',
            'velmi', 'dobrý', 'jsme', 'bylo', 'jsou'
        ]

        first_words = text_lower.split()[:5]
        for word in first_words:
            if word in non_english_markers:
                return False

        english_markers = [
            'the', 'was', 'very', 'great', 'nice', 'good', 'we', 'our', 'had',
            'place', 'location', 'stay', 'apartment', 'host', 'clean',
            'would', 'recommend'
        ]

        english_count = sum(1 for word in text_lower.split() if word in english_markers)
        return english_count >= 2

    def calculate_sentiment(self, comments):
        if pd.isna(comments) or comments == '':
            return 0.0
        try:
            scores = self.vader.polarity_scores(str(comments))
            return scores['compound']
        except Exception:
            return 0.0

    def categorize_sentiment(self, score):
        if score >= 0.30:
            return 'positive'
        elif score <= -0.30:
            return 'negative'
        else:
            return 'neutral'

    def process_reviews(self):
        print(f"Processing {self.city} reviews sentiment...")

        reviews_path = self.raw_path / 'reviews.csv'
        if not reviews_path.exists():
            print(f"⚠️  No reviews.csv in {self.raw_path}")
            return pd.DataFrame()

        reviews = pd.read_csv(reviews_path)
        print(f"  Total reviews: {len(reviews):,}")

        listings_path = self.processed_path / 'listings_clean.csv'
        if not listings_path.exists():
            print(f"❌ Run data_etl.py {self.city} first!")
            return pd.DataFrame()

        listings = pd.read_csv(listings_path)
        valid_listings = set(listings['listing_id'])

        reviews = reviews[reviews['listing_id'].isin(valid_listings)]
        print(f"  Reviews for processed listings: {len(reviews):,}")

        print("  Filtering for English reviews...")
        reviews['is_english'] = reviews['comments'].apply(self.is_likely_english)
        reviews = reviews[reviews['is_english'] == True]
        print(f"  English reviews: {len(reviews):,}")

        if reviews.empty:
            print(f"⚠️  No English reviews found for {self.city}")
            return pd.DataFrame()

        print("  Analyzing sentiment (this takes time)...")
        reviews['sentiment'] = reviews['comments'].apply(self.calculate_sentiment)
        reviews['sentiment_category'] = reviews['sentiment'].apply(self.categorize_sentiment)

        output_file = self.processed_path / 'reviews_sentiment.csv'
        reviews[['listing_id', 'id', 'date', 'sentiment', 'sentiment_category']].to_csv(
            output_file, index=False
        )
        print(f"✓ Saved: {output_file} ({len(reviews):,} reviews)")

        return reviews

    def create_listing_sentiment(self, reviews):
        print("Aggregating sentiment per listing...")

        listing_sentiment = reviews.groupby('listing_id').agg({
            'sentiment': ['mean', 'std', 'min', 'max', 'count']
        }).reset_index()

        listing_sentiment.columns = [
            'listing_id', 'sentiment_mean', 'sentiment_std',
            'sentiment_min', 'sentiment_max', 'review_count'
        ]

        listing_sentiment['sentiment_std'] = listing_sentiment['sentiment_std'].fillna(0)
        listing_sentiment['city'] = self.city

        output_file = self.processed_path / 'listing_sentiment.csv'
        listing_sentiment.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file} ({len(listing_sentiment):,} listings)")

        return listing_sentiment

    def create_neighborhood_sentiment(self, reviews):
        print("Creating neighborhood sentiment stats...")

        listings = pd.read_csv(self.processed_path / 'listings_clean.csv')

        reviews_with_neighborhood = reviews.merge(
            listings[['listing_id', 'neighborhood']],
            on='listing_id',
            how='inner'
        )

        print(f"  Reviews with neighborhood: {len(reviews_with_neighborhood):,}")

        neighborhood_sentiment = reviews_with_neighborhood.groupby('neighborhood')['sentiment'].agg([
            'mean', 'median', 'std', 'count'
        ]).reset_index()

        neighborhood_sentiment.columns = [
            'neighborhood', 'sentiment_mean', 'sentiment_median',
            'sentiment_std', 'total_reviews'
        ]

        neighborhood_sentiment['sentiment_std'] = neighborhood_sentiment['sentiment_std'].fillna(0)

        sentiment_dist = (
            reviews_with_neighborhood
            .groupby(['neighborhood', 'sentiment_category'])
            .size()
            .unstack(fill_value=0)
        )

        sentiment_dist = sentiment_dist.div(sentiment_dist.sum(axis=1), axis=0) * 100
        sentiment_dist = sentiment_dist.reset_index()

        neighborhood_sentiment = neighborhood_sentiment.merge(
            sentiment_dist,
            on='neighborhood',
            how='left'
        )

        neighborhood_sentiment['city'] = self.city

        output_file = self.processed_path / 'neighborhood_sentiment.csv'
        neighborhood_sentiment.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file} ({len(neighborhood_sentiment):,} neighborhoods)")

        return neighborhood_sentiment

    def create_listings_map(self):
        print("Creating map data with sentiment...")

        listings = pd.read_csv(self.processed_path / 'listings_clean.csv')
        listing_sentiment = pd.read_csv(self.processed_path / 'listing_sentiment.csv')

        map_data = listings.merge(listing_sentiment, on='listing_id', how='left')

        map_data['sentiment_mean'] = map_data['sentiment_mean'].fillna(0)
        map_data['sentiment_category'] = map_data['sentiment_mean'].apply(self.categorize_sentiment)

        map_cols = [
            'listing_id', 'listing_name', 'latitude', 'longitude',
            'price', 'room_type', 'neighborhood',
            'sentiment_mean', 'sentiment_category', 'review_count'
        ]

        map_data = map_data[map_cols]
        map_data['city'] = self.city

        output_file = self.processed_path / 'listings_map.csv'
        map_data.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file} ({len(map_data):,} listings)")

        return map_data

    def run(self):
        print("=" * 60)
        print(f"SENTIMENT ETL: {self.city.upper()}")
        print("=" * 60)

        reviews = self.process_reviews()
        if reviews.empty:
            print(f"⚠️  No data processed for {self.city}")
            return

        self.create_listing_sentiment(reviews)
        self.create_neighborhood_sentiment(reviews)
        self.create_listings_map()

        print(f"\n✓ {self.city.upper()} SENTIMENT ETL COMPLETE!\n")


def main(cities=None):
    """
    Callable entrypoint for pipeline imports.
    Still supports running this file directly.
    """
    if cities is None:
        cities = ['amsterdam', 'rome', 'prague', 'sicily', 'bordeaux', 'crete']

    for city in cities:
        etl = SentimentETL(city)
        etl.run()
        print()


if __name__ == "__main__":
    main()
