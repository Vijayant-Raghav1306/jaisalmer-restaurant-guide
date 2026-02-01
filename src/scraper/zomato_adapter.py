"""
Zomato Dataset Adapter
Converts Zomato dataset to our format
Filters for relevant Indian/Rajasthani restaurants
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from src.scraper.utils import save_json, clean_text


class ZomatoAdapter:
    """Adapt Zomato dataset to our format"""
    
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.df = None
        
    def load_dataset(self):
        """Load the Zomato CSV file"""
        try:
            print(f"📂 Loading dataset from: {self.csv_path}")
            
            # Try different encodings
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    self.df = pd.read_csv(self.csv_path, encoding=encoding)
                    print(f"✅ Loaded with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if self.df is None:
                raise Exception("Could not load file with any encoding")
            
            print(f"✅ Dataset loaded: {len(self.df)} rows, {len(self.df.columns)} columns")
            print(f"\n📊 Columns: {', '.join(self.df.columns.tolist())}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return False
    
    def explore_dataset(self):
        """Show dataset statistics"""
        if self.df is None:
            print("❌ No dataset loaded")
            return
        
        print("\n" + "="*60)
        print("DATASET EXPLORATION")
        print("="*60)
        
        print(f"\nTotal records: {len(self.df)}")
        print(f"\nSample data:")
        print(self.df.head())
        
        # Show unique values for key columns
        if 'City' in self.df.columns:
            print(f"\nUnique cities: {self.df['City'].nunique()}")
            print(f"Top cities: {self.df['City'].value_counts().head()}")
        
        if 'Cuisines' in self.df.columns:
            print(f"\nSample cuisines: {self.df['Cuisines'].head()}")
        
        if 'Rating text' in self.df.columns:
            print(f"\nRating distribution:")
            print(self.df['Rating text'].value_counts())
    
    def filter_indian_restaurants(self, max_restaurants=50):
        """Filter for Indian/Rajasthani restaurants"""
        if self.df is None:
            return None
        
        print("\n" + "="*60)
        print("FILTERING RESTAURANTS")
        print("="*60)
        
        filtered = self.df.copy()
        
        # Filter by cuisine (if column exists)
        if 'Cuisines' in filtered.columns:
            print("\n🔍 Filtering by Indian/Rajasthani cuisine...")
            cuisine_keywords = ['Indian', 'Rajasthani', 'North Indian', 
                              'Vegetarian', 'Mughlai']
            
            mask = filtered['Cuisines'].fillna('').str.contains(
                '|'.join(cuisine_keywords), 
                case=False, 
                na=False
            )
            filtered = filtered[mask]
            print(f"   Found {len(filtered)} restaurants")
        
        # Filter by rating (if column exists)
        if 'Aggregate rating' in filtered.columns:
            print("\n⭐ Filtering by rating (>= 3.5)...")
            filtered = filtered[filtered['Aggregate rating'] >= 3.5]
            print(f"   Found {len(filtered)} restaurants")
        
        # Filter by country (if column exists)
        if 'Country Code' in filtered.columns:
            print("\n🇮🇳 Filtering by India...")
            filtered = filtered[filtered['Country Code'] == 1]  # 1 = India
            print(f"   Found {len(filtered)} restaurants")
        
        # Take top rated
        if 'Aggregate rating' in filtered.columns:
            filtered = filtered.nlargest(max_restaurants, 'Aggregate rating')
        else:
            filtered = filtered.head(max_restaurants)
        
        print(f"\n✅ Final count: {len(filtered)} restaurants")
        return filtered
    
    def generate_review_from_row(self, row):
        """
        Generate a review-like text from restaurant data
        Since Zomato dataset might not have review text,
        we create descriptive text from available fields
        """
        reviews = []
        
        # Check if there's actual review text
        if 'Review' in row.index and pd.notna(row['Review']) and row['Review']:
            reviews.append({
                "text": clean_text(str(row['Review'])),
                "rating": int(row.get('Rating', 4)),
                "author": "Zomato User",
                "date": "2024-01-01",
                "source": "zomato"
            })
        else:
            # Generate synthetic review from data
            rating = row.get('Aggregate rating', 4)
            cuisines = row.get('Cuisines', 'Indian')
            
            # Create descriptive text based on rating
            if rating >= 4.5:
                templates = [
                    f"Excellent {cuisines} restaurant with authentic flavors. Highly recommended for traditional cuisine lovers.",
                    f"Outstanding food quality and service. The {cuisines} dishes are prepared with great care and taste amazing.",
                    f"One of the best places for {cuisines} food. Fresh ingredients and authentic recipes make this a must-visit."
                ]
            elif rating >= 4.0:
                templates = [
                    f"Good {cuisines} restaurant with tasty food. Worth trying for authentic flavors.",
                    f"Nice place for {cuisines} cuisine. Food is well-prepared and portions are generous.",
                    f"Decent restaurant serving {cuisines} food. Good taste and reasonable prices."
                ]
            elif rating >= 3.5:
                templates = [
                    f"Average {cuisines} restaurant. Food is okay but nothing extraordinary.",
                    f"Decent option for {cuisines} food. Service could be better but food is acceptable.",
                ]
            else:
                return []
            
            import random
            text = random.choice(templates)
            
            reviews.append({
                "text": text,
                "rating": int(rating),
                "author": "Zomato User",
                "date": "2024-01-01",
                "source": "zomato_synthetic"
            })
        
        return reviews
    
    def convert_to_our_format(self, filtered_df):
        """Convert filtered dataframe to our restaurant format"""
        restaurants = []
        
        print("\n" + "="*60)
        print("CONVERTING TO OUR FORMAT")
        print("="*60)
        
        for idx, row in filtered_df.iterrows():
            # Extract basic info
            name = row.get('Restaurant Name', f"Restaurant {idx}")
            rating = row.get('Aggregate rating', 0)
            cuisines = row.get('Cuisines', '').split(', ') if pd.notna(row.get('Cuisines')) else []
            
            # Price range
            price_range = "₹₹"
            if 'Price range' in row.index:
                price_val = row['Price range']
                if price_val == 1:
                    price_range = "₹"
                elif price_val == 2:
                    price_range = "₹₹"
                elif price_val >= 3:
                    price_range = "₹₹₹"
            
            # Generate reviews
            reviews = self.generate_review_from_row(row)
            
            restaurant = {
                "name": clean_text(str(name)),
                "rating": float(rating),
                "cuisine": cuisines,
                "price_range": price_range,
                "reviews": reviews,
                "source": "zomato_dataset"
            }
            
            restaurants.append(restaurant)
            print(f"  ✅ {restaurant['name']} ({len(reviews)} reviews)")
        
        return restaurants
    
    def adapt_dataset(self, max_restaurants=30):
        """Main function to adapt the dataset"""
        print("="*60)
        print("ZOMATO DATASET ADAPTER")
        print("="*60)
        
        # Load dataset
        if not self.load_dataset():
            return None
        
        # Explore (optional - comment out if not needed)
        # self.explore_dataset()
        
        # Filter restaurants
        filtered = self.filter_indian_restaurants(max_restaurants)
        
        if filtered is None or len(filtered) == 0:
            print("\n❌ No restaurants after filtering")
            return None
        
        # Convert to our format
        restaurants = self.convert_to_our_format(filtered)
        
        # Create output
        output = {
            "metadata": {
                "source": "zomato_dataset",
                "original_records": len(self.df) if self.df is not None else 0,
                "filtered_records": len(filtered),
                "collection_date": datetime.now().strftime("%Y-%m-%d"),
                "total_restaurants": len(restaurants),
                "total_reviews": sum(len(r["reviews"]) for r in restaurants)
            },
            "restaurants": restaurants
        }
        
        return output


def main():
    """Main execution"""
    
    print("="*60)
    print("ZOMATO DATASET ADAPTER")
    print("="*60)
    
    # Path to your downloaded Zomato CSV
    # UPDATE THIS PATH to where you downloaded the file
    csv_path = "data/raw/zomato.csv"  # Change this!
    
    if not Path(csv_path).exists():
        print(f"\n❌ File not found: {csv_path}")
        print("\n📋 Instructions:")
        print("1. Download the Zomato dataset from Kaggle")
        print("2. Save it to: data/raw/zomato.csv")
        print("3. Update the 'csv_path' variable in this script")
        print("4. Run again")
        return
    
    # Create adapter
    adapter = ZomatoAdapter(csv_path)
    
    # Adapt dataset
    output = adapter.adapt_dataset(max_restaurants=30)
    
    if output:
        # Save
        output_file = "data/raw/zomato_adapted.json"
        save_json(output, output_file)
        
        print("\n" + "="*60)
        print("✅ DATASET ADAPTED SUCCESSFULLY!")
        print("="*60)
        print(f"Restaurants: {output['metadata']['total_restaurants']}")
        print(f"Reviews: {output['metadata']['total_reviews']}")
        print(f"Saved to: {output_file}")
        print("="*60)
    else:
        print("\n❌ Adaptation failed")


if __name__ == "__main__":
    main()
    