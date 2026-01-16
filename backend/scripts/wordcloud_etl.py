#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
import re
from nltk.corpus import stopwords
import nltk
from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt


# Download stopwords once
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


class WordCloudETL:
    """
    Extract top words from ENGLISH reviews for word cloud visualization
    Generates: CSV data + PNG images
    Requires: data_etl.py run first (creates listings_clean.csv)
    """

    def __init__(self, city):
        self.city = city
        self.raw_path = Path(f'../data/raw/{city}')
        self.processed_path = Path(f'../data/processed/{city}')
        self.images_path = self.processed_path / 'wordcloud_images'
        self.images_path.mkdir(exist_ok=True)

        self.stop_words = set(stopwords.words('english'))

        # Common Airbnb words to filter out
        self.stop_words.update([
            'apartment', 'room', 'place', 'stay', 'flat', 'house',
            'host', 'airbnb', 'booking', 'location', 'area', 'great',
            'good', 'nice', 'also', 'really', 'would', 'highly',
            'stayed', 'perfect', 'recommend', 'excellent', 'amsterdam',
            'rome', 'prague', 'everything', 'appartment', 'restaurants',
            'molto', 'amazing', 'para', 'pour', 'sehr', 'many', 'casa',
            'roma', 'zona', 'time', 'posizione', 'todo', 'paolo', 'definitely',
            'thank', 'staff', 'next', 'super', 'hotel', 'close', 'walk',
            'clean', 'comfortable', 'easy', 'beautiful', 'walking', 'centro'
        ])

    def is_likely_english(self, text):
        """Same filter as sentiment_etl.py - only process English reviews"""
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

    def clean_text(self, text):
        """Extract meaningful words from review text"""
        if pd.isna(text) or text == '':
            return []

        text = str(text).lower()
        text = re.sub(r'[^a-z\s]', ' ', text)

        words = text.split()
        words = [w for w in words if len(w) > 3 and w not in self.stop_words]
        return words

    def generate_wordcloud_image(self, word_freq, filename, title):
        """Generate a single wordcloud PNG image"""
        if not word_freq:
            return

        wc = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            colormap='viridis',
            max_words=100,
            relative_scaling=0.5
        ).generate_from_frequencies(word_freq)

        plt.figure(figsize=(15, 7.5))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title(title, fontsize=20, pad=20)
        plt.tight_layout(pad=0)
        plt.savefig(self.images_path / filename, dpi=150, bbox_inches='tight')
        plt.close()

    def process_reviews(self):
        print(f"Processing {self.city} word frequencies (English only)...")

        reviews_path = self.raw_path / 'reviews.csv'
        if not reviews_path.exists():
            print(f"⚠️  No reviews.csv in {self.raw_path}")
            return pd.DataFrame()

        reviews = pd.read_csv(reviews_path)
        total_before = len(reviews)
        print(f"  Total reviews: {total_before:,}")

        listings_path = self.processed_path / 'listings_clean.csv'
        if not listings_path.exists():
            print("❌ Run data_etl.py first!")
            return pd.DataFrame()

        listings = pd.read_csv(listings_path)

        # Merge to get neighborhoods
        reviews = reviews.merge(
            listings[['listing_id', 'neighborhood']],
            on='listing_id',
            how='inner'
        )

        # Filter for English
        print("  Filtering for English reviews...")
        reviews['is_english'] = reviews['comments'].apply(self.is_likely_english)
        english_count = int(reviews['is_english'].sum())
        reviews = reviews[reviews['is_english'] == True]
        total_after = len(reviews)

        pct = (english_count / max(total_before, 1)) * 100
        print(f"  English reviews: {total_after:,} ({pct:.1f}% of raw)")

        if reviews.empty:
            print(f"⚠️  No English reviews found for {self.city}")
            return pd.DataFrame()

        print(f"  Extracting words from {len(reviews):,} English reviews...")

        results = []
        image_count = 0

        for neighborhood in reviews['neighborhood'].dropna().unique():
            neighborhood_reviews = reviews[reviews['neighborhood'] == neighborhood]

            all_words = []
            for comment in neighborhood_reviews['comments'].dropna():
                all_words.extend(self.clean_text(comment))

            word_counts = Counter(all_words)

            # Top 100 words per neighborhood
            for word, freq in word_counts.most_common(100):
                results.append({
                    'city': self.city,
                    'neighborhood': neighborhood,
                    'word': word,
                    'frequency': int(freq)
                })

            # Generate image if enough words
            if len(word_counts) > 10:
                word_freq = dict(word_counts.most_common(100))
                safe_name = str(neighborhood).replace('/', '_').replace(' ', '_')
                filename = f'{safe_name}.png'
                title = f'{neighborhood} - {self.city.title()}'
                self.generate_wordcloud_image(word_freq, filename, title)
                image_count += 1

        print(f"  ✓ Generated {image_count} neighborhood wordcloud images")

        # City-level (all neighborhoods combined)
        print("  Creating city-level word cloud...")
        all_words = []
        for comment in reviews['comments'].dropna():
            all_words.extend(self.clean_text(comment))

        word_counts = Counter(all_words)
        for word, freq in word_counts.most_common(200):
            results.append({
                'city': self.city,
                'neighborhood': None,
                'word': word,
                'frequency': int(freq)
            })

        word_freq = dict(word_counts.most_common(100))
        self.generate_wordcloud_image(
            word_freq,
            f'{self.city}_overall.png',
            f'{self.city.title()} - All English Reviews'
        )

        df = pd.DataFrame(results)

        output_file = self.processed_path / 'review_words.csv'
        df.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file} ({len(df):,} words)")

        return df

    def run(self):
        print("=" * 60)
        print(f"WORD CLOUD ETL: {self.city.upper()}")
        print("=" * 60)

        words = self.process_reviews()
        if words.empty:
            print(f"⚠️  No data processed for {self.city}")
            return

        print(f"\n✓ {self.city.upper()} WORD CLOUD ETL COMPLETE!")
        print(f"  → CSV: {self.processed_path / 'review_words.csv'}")
        print(f"  → Images: {self.images_path}/\n")


def main(cities=None):
    """Callable entrypoint for pipeline imports."""
    if cities is None:
        cities = ['amsterdam', 'rome', 'prague']

    for city in cities:
        etl = WordCloudETL(city)
        etl.run()
        print()


if __name__ == "__main__":
    main()
