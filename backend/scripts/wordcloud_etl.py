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
    Extract top words from reviews for word cloud visualization
    Generates: CSV data + PNG images
    Requires: sentiment_etl.py run first (creates reviews_sentiment.csv)
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
            'rome', 'prague', 'everything', 'appartment', 'retaurants',
            'molto', 'amazing', 'para', 'pour', 'sehr', 'many', 'casa',
            'roma', 'zona', 'time', 'posizione', 'todo', 'paolo','definitely',
            'thank', 'staff', 'next', 'many', 'super', 'hotel'
        ])
    
    def clean_text(self, text):
        """Extract meaningful words from review text"""
        if pd.isna(text) or text == '':
            return []
        
        # Lowercase and remove special chars
        text = str(text).lower()
        text = re.sub(r'[^a-z\s]', ' ', text)
        
        # Split and filter
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
        print(f"Processing {self.city} word frequencies...")
        
        # Load reviews
        reviews_path = self.raw_path / 'reviews.csv'
        if not reviews_path.exists():
            print(f"⚠️  No reviews.csv in {self.raw_path}")
            return pd.DataFrame()
        
        # Load processed listings to get neighborhoods
        listings_path = self.processed_path / 'listings_clean.csv'
        if not listings_path.exists():
            print(f"❌ Run data_etl.py first!")
            return pd.DataFrame()
        
        reviews = pd.read_csv(reviews_path)
        listings = pd.read_csv(listings_path)
        
        # Merge to get neighborhoods
        reviews = reviews.merge(
            listings[['listing_id', 'neighbourhood']], 
            on='listing_id',
            how='inner'
        )
        
        print(f"  Analyzing {len(reviews):,} reviews...")
        
        # Extract words by neighborhood
        results = []
        image_count = 0
        
        for neighbourhood in reviews['neighbourhood'].unique():
            hood_reviews = reviews[reviews['neighbourhood'] == neighbourhood]
            
            # Combine all comments
            all_words = []
            for comment in hood_reviews['comments'].dropna():
                all_words.extend(self.clean_text(comment))
            
            # Count frequencies
            word_counts = Counter(all_words)
            
            # Top 100 words per neighborhood
            for word, freq in word_counts.most_common(100):
                results.append({
                    'city': self.city,
                    'neighbourhood': neighbourhood,
                    'word': word,
                    'frequency': freq
                })
            
            # Generate image for this neighborhood
            if len(word_counts) > 10:  # Only if enough words
                word_freq = dict(word_counts.most_common(100))
                safe_name = neighbourhood.replace('/', '_').replace(' ', '_')
                filename = f'{safe_name}.png'
                title = f'{neighbourhood} - {self.city.title()}'
                self.generate_wordcloud_image(word_freq, filename, title)
                image_count += 1
        
        print(f"  ✓ Generated {image_count} neighborhood wordcloud images")
        
        # City-level (all neighborhoods combined)
        print(f"  Creating city-level word cloud...")
        all_words = []
        for comment in reviews['comments'].dropna():
            all_words.extend(self.clean_text(comment))
        
        word_counts = Counter(all_words)
        for word, freq in word_counts.most_common(200):
            results.append({
                'city': self.city,
                'neighbourhood': None,  # City-level
                'word': word,
                'frequency': freq
            })
        
        # Generate city-level image
        word_freq = dict(word_counts.most_common(100))
        self.generate_wordcloud_image(word_freq, f'{self.city}_overall.png', f'{self.city.title()} - All Reviews')
        
        df = pd.DataFrame(results)
        
        output_file = self.processed_path / 'review_words.csv'
        df.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file} ({len(df)} words)")
        
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


if __name__ == "__main__":
    cities = ['amsterdam', 'rome', 'prague']
    
    for city in cities:
        etl = WordCloudETL(city)
        etl.run()
        print()
