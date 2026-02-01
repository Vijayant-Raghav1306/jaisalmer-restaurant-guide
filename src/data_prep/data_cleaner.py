"""
Data Cleaner
Cleans and prepares the combined dataset for RAG
"""

import json
import re
from pathlib import Path
from datetime import datetime
from src.scraper.utils import save_json, load_json, clean_text


class DataCleaner:
    """Clean and prepare data for embedding"""
    
    def __init__(self, input_file):
        self.input_file = input_file
        self.data = None
        self.stats = {
            "original_restaurants": 0,
            "original_reviews": 0,
            "cleaned_restaurants": 0,
            "cleaned_reviews": 0,
            "duplicates_removed": 0,
            "short_reviews_removed": 0,
            "long_reviews_split": 0
        }
    
    def load_data(self):
        """Load the combined dataset"""
        print("="*60)
        print("DATA CLEANER")
        print("="*60)
        
        print(f"\n📂 Loading data from: {self.input_file}")
        self.data = load_json(self.input_file)
        
        if not self.data:
            raise Exception("Could not load data file")
        
        restaurants = self.data.get("restaurants", [])
        self.stats["original_restaurants"] = len(restaurants)
        self.stats["original_reviews"] = sum(
            len(r.get("reviews", [])) for r in restaurants
        )
        
        print(f"✅ Loaded: {self.stats['original_restaurants']} restaurants")
        print(f"✅ Total reviews: {self.stats['original_reviews']}")
    
    def clean_review_text(self, text):
        """Clean a single review text"""
        if not text:
            return ""
        
        # Convert to string
        text = str(text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
        
        # Fix common issues
        text = text.replace('...', '.')
        text = text.replace('!!', '!')
        text = text.replace('??', '?')
        
        return text.strip()
    
    def is_review_valid(self, review):
        """Check if review meets quality criteria"""
        text = review.get("text", "")
        
        # Too short
        if len(text) < 30:
            return False, "too_short"
        
        # Too generic
        generic_phrases = ["good", "nice", "ok", "fine", "average"]
        if text.lower().strip() in generic_phrases:
            return False, "too_generic"
        
        # Has actual content
        word_count = len(text.split())
        if word_count < 5:
            return False, "too_few_words"
        
        return True, "valid"
    
    def remove_duplicate_reviews(self, reviews):
        """Remove duplicate reviews based on text similarity"""
        unique_reviews = []
        seen_fingerprints = set()
        
        for review in reviews:
            text = review.get("text", "")
            
            # Create fingerprint (first 100 chars, lowercase, no spaces)
            fingerprint = ''.join(text[:100].lower().split())
            
            if fingerprint and fingerprint not in seen_fingerprints:
                seen_fingerprints.add(fingerprint)
                unique_reviews.append(review)
            else:
                self.stats["duplicates_removed"] += 1
        
        return unique_reviews
    
    def clean_restaurant(self, restaurant):
        """Clean a single restaurant's data"""
        cleaned_restaurant = {
            "name": restaurant.get("name", "Unknown"),
            "rating": float(restaurant.get("rating", 0)),
            "cuisine": restaurant.get("cuisine", []),
            "price_range": restaurant.get("price_range", "₹₹"),
            "address": restaurant.get("address", ""),
            "phone": restaurant.get("phone", ""),
            "reviews": []
        }
        
        # Ensure cuisine is a list
        if isinstance(cleaned_restaurant["cuisine"], str):
            cleaned_restaurant["cuisine"] = [cleaned_restaurant["cuisine"]]
        
        # Clean reviews
        reviews = restaurant.get("reviews", [])
        
        for review in reviews:
            # Clean text
            cleaned_text = self.clean_review_text(review.get("text", ""))
            
            if not cleaned_text:
                continue
            
            # Create cleaned review
            cleaned_review = {
                "text": cleaned_text,
                "rating": int(review.get("rating", 0)),
                "author": review.get("author", "Anonymous"),
                "date": review.get("date", ""),
                "source": review.get("source", "unknown")
            }
            
            # Validate
            is_valid, reason = self.is_review_valid(cleaned_review)
            
            if is_valid:
                cleaned_restaurant["reviews"].append(cleaned_review)
            else:
                if reason == "too_short":
                    self.stats["short_reviews_removed"] += 1
        
        # Remove duplicates
        cleaned_restaurant["reviews"] = self.remove_duplicate_reviews(
            cleaned_restaurant["reviews"]
        )
        
        return cleaned_restaurant
    
    def clean_all_data(self):
        """Clean all restaurants and reviews"""
        print("\n" + "="*60)
        print("CLEANING DATA")
        print("="*60)
        
        cleaned_restaurants = []
        
        if not self.data:
            raise Exception("Data not loaded. Call load_data() first.")
        
        for restaurant in self.data.get("restaurants", []):
            cleaned = self.clean_restaurant(restaurant)
            
            # Only keep restaurants with at least 1 review
            if cleaned["reviews"]:
                cleaned_restaurants.append(cleaned)
                print(f"  ✅ {cleaned['name']}: {len(cleaned['reviews'])} reviews")
            else:
                print(f"  ❌ Skipped {cleaned['name']}: No valid reviews")
        
        self.stats["cleaned_restaurants"] = len(cleaned_restaurants)
        self.stats["cleaned_reviews"] = sum(
            len(r["reviews"]) for r in cleaned_restaurants
        )
        
        return cleaned_restaurants
    
    def create_cleaned_dataset(self, cleaned_restaurants):
        """Create final cleaned dataset"""
        cleaned_data = {
            "metadata": {
                "source": "cleaned_data",
                "original_file": self.input_file,
                "cleaning_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_restaurants": len(cleaned_restaurants),
                "total_reviews": sum(len(r["reviews"]) for r in cleaned_restaurants),
                "cleaning_stats": self.stats
            },
            "restaurants": cleaned_restaurants
        }
        
        return cleaned_data
    
    def clean(self):
        """Main cleaning process"""
        # Load data
        self.load_data()
        
        # Clean
        cleaned_restaurants = self.clean_all_data()
        
        # Create final dataset
        cleaned_data = self.create_cleaned_dataset(cleaned_restaurants)
        
        # Print statistics
        print("\n" + "="*60)
        print("CLEANING STATISTICS")
        print("="*60)
        print(f"\nBefore:")
        print(f"  Restaurants: {self.stats['original_restaurants']}")
        print(f"  Reviews: {self.stats['original_reviews']}")
        
        print(f"\nAfter:")
        print(f"  Restaurants: {self.stats['cleaned_restaurants']}")
        print(f"  Reviews: {self.stats['cleaned_reviews']}")
        
        print(f"\nRemoved:")
        print(f"  Duplicates: {self.stats['duplicates_removed']}")
        print(f"  Too short: {self.stats['short_reviews_removed']}")
        
        efficiency = (self.stats['cleaned_reviews'] / self.stats['original_reviews'] * 100) if self.stats['original_reviews'] > 0 else 0
        print(f"\nRetention rate: {efficiency:.1f}%")
        print("="*60)
        
        return cleaned_data


def main():
    """Main execution"""
    
    input_file = "data/processed/final_dataset.json"
    output_file = "data/processed/cleaned_dataset.json"
    
    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        print("\nMake sure you've run:")
        print("python src/scraper/combine_all_sources.py")
        return
    
    # Create cleaner
    cleaner = DataCleaner(input_file)
    
    # Clean data
    cleaned_data = cleaner.clean()
    
    # Save
    save_json(cleaned_data, output_file)
    
    print(f"\n✅ Cleaned data saved to: {output_file}")
    print("\n⏭️  Next step: Create documents for embedding")


if __name__ == "__main__":
    main()

